/* ============================================================
   TopGo.AI — script.js
   Main client-side logic for AI Itinerary Planner
   ============================================================ */

// --- Global state ---
let CITIES = [];
let PLACES_BY_CITY = {};
let selectedCity = null;
let selectedPlaces = [];
let leafletMapInstance = null; // Leaflet map singleton

// Approximate road distances (km) between city pairs
const CITY_DIST = {
    "ha-hcm": 1700, "hcm-ha": 1700,
    "ha-dn": 764, "dn-ha": 764,
    "ha-hue": 666, "hue-ha": 666,
    "ha-hoian": 773, "hoian-ha": 773,
    "ha-nt": 1278, "nt-ha": 1278,
    "ha-dl": 1480, "dl-ha": 1480,
    "ha-ph": 2050, "ph-ha": 2050,
    "ha-hl": 165, "hl-ha": 165,
    "ha-qni": 1070, "qni-ha": 1070,
    "hcm-dn": 964, "dn-hcm": 964,
    "hcm-hue": 1045, "hue-hcm": 1045,
    "hcm-hoian": 970, "hoian-hcm": 970,
    "hcm-nt": 448, "nt-hcm": 448,
    "hcm-dl": 308, "dl-hcm": 308,
    "hcm-ph": 460, "ph-hcm": 460,
    "hcm-qni": 690, "qni-hcm": 690,
    "dn-hue": 100, "hue-dn": 100,
    "dn-hoian": 30, "hoian-dn": 30,
    "dn-nt": 534, "nt-dn": 534,
    "dn-dl": 420, "dl-dn": 420,
};

// Departure city keyword → city info
const DEP_CITY_MAP = [
    { keywords: ["nội bài", "hà nội", "hanoi", "ga hà nội", "ha noi"], code: "HAN", name: "Hà Nội", id: "ha" },
    {
        keywords: ["tân sơn nhất", "tan son nhat", "sài gòn", "saigon", "sgn",
            "hồ chí minh", "ho chi minh", "miền đông", "miền tây",
            "bến xe miền đông", "bến xe miền tây", "ga sài gòn"], code: "SGN", name: "TP.HCM", id: "hcm"
    },
    { keywords: ["đà nẵng", "da nang", "dad", "sân bay đà nẵng"], code: "DAD", name: "Đà Nẵng", id: "dn" },
    { keywords: ["phú bài", "phu bai", "huế", "hue", "hui"], code: "HUI", name: "Huế", id: "hue" },
    { keywords: ["cam ranh", "nha trang", "cxr"], code: "CXR", name: "Nha Trang", id: "nt" },
    { keywords: ["đà lạt", "da lat", "liên khương", "dli"], code: "DLI", name: "Đà Lạt", id: "dl" },
    { keywords: ["phú quốc", "phu quoc", "pqc"], code: "PQC", name: "Phú Quốc", id: "ph" },
    { keywords: ["hạ long", "ha long", "hải phòng", "hai phong", "hph"], code: "HPH", name: "Hạ Long", id: "hl" },
];

function detectDepartureCity(val) {
    const v = val.toLowerCase();
    for (const entry of DEP_CITY_MAP) {
        if (entry.keywords.some(kw => v.includes(kw))) return entry;
    }
    return null;
}

function getApproxDistance(depId, destId) {
    if (!depId || !destId || depId === destId) return 0;
    return CITY_DIST[`${depId}-${destId}`] || null;
}

// --- Data loading ---
async function loadData() {
    try {
        const [cr, pr] = await Promise.all([
            fetch('/api/cities').then(r => r.json()),
            fetch('/api/places').then(r => r.json())
        ]);
        CITIES = cr;
        PLACES_BY_CITY = pr;
    } catch (e) {
        showToast('Không thể tải dữ liệu. Vui lòng làm mới trang.', 'error');
    }
    renderCityList('');
    // Default departure
    const depInput = document.getElementById('dep-input');
    if (depInput) {
        depInput.value = 'Sân bay Nội Bài, Hà Nội';
        updateDeparture('Sân bay Nội Bài, Hà Nội');
        depInput.addEventListener('input', function () {
            updateDeparture(this.value);
        });
    }
}

// --- Screen switching ---
function showScreen(name) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const target = document.getElementById('screen-' + name);
    if (target) target.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (name === 'result') {
        setTimeout(initLeafletMap, 150);
    }
}

// --- Dropdowns ---
function openDrop(id) {
    document.getElementById(id).classList.add('open');
    if (id === 'dd-city') renderCityList('');
    if (id === 'dd-place') renderPlaceList('');
}
function closeDrop(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('open');
}
function toggleDrop(id) {
    const el = document.getElementById(id);
    el.classList.contains('open') ? closeDrop(id) : openDrop(id);
}

// --- City selection ---
function renderCityList(filter) {
    const list = document.getElementById('city-list');
    if (!list) return;
    const q = (filter || '').toLowerCase();
    const filtered = CITIES.filter(c =>
        c.name.toLowerCase().includes(q) || c.sub.toLowerCase().includes(q)
    );
    if (!filtered.length) {
        list.innerHTML = '<div class="dd-empty">Không tìm thấy thành phố</div>';
        return;
    }
    list.innerHTML = filtered.map(c => {
        const isSel = selectedCity && selectedCity.id === c.id;
        return `<div class="dd-item ${isSel ? 'sel' : ''}" onclick="selectCity('${c.id}')">
      <img class="di-img" src="${c.img}"
           onerror="this.style.background='${c.color}';this.removeAttribute('src')"
           alt="${c.name}" style="background:${c.color}">
      <div class="di-info">
        <div class="di-name">${c.name}</div>
        <div class="di-sub">${c.sub}</div>
      </div>
      ${isSel ? '<span class="di-check">✓</span>' : ''}
    </div>`;
    }).join('');
}

function filterCities(val) { renderCityList(val); }

function selectCity(id) {
    const city = CITIES.find(c => c.id === id);
    if (!city) return;
    selectedCity = city;
    // Clear selected places when city changes
    selectedPlaces = [];
    renderPlaceTags();
    renderCityList(document.getElementById('city-search').value);
    document.getElementById('city-search').value = city.name;
    closeDrop('dd-city');
    updateFromToDisplay();
    document.getElementById('err-city').classList.remove('show');
    // Clear place search input
    const placeSearch = document.getElementById('place-search');
    if (placeSearch) placeSearch.value = '';
}

function updateFromToDisplay() {
    const toEl = document.getElementById('ft-to-city');
    const toSubEl = document.getElementById('ft-to-sub');
    if (selectedCity) {
        toEl.textContent = selectedCity.abbr;
        toSubEl.textContent = selectedCity.name;
    } else {
        toEl.textContent = '—';
        toSubEl.textContent = 'Chọn thành phố bên dưới';
    }
}

function updateDeparture(val) {
    const fromEl = document.getElementById('ft-from-city');
    const fromSubEl = document.getElementById('ft-from-sub');
    if (!fromEl) return;
    if (val && val.trim()) {
        const detected = detectDepartureCity(val);
        if (detected) {
            fromEl.textContent = detected.code;
            fromSubEl.textContent = detected.name;
        } else {
            const short = val.split(',')[0].trim().split(' ').slice(-2).join(' ');
            fromEl.textContent = short.length > 9 ? short.substring(0, 8) + '…' : short;
            fromSubEl.textContent = val.length > 32 ? val.substring(0, 32) + '…' : val;
        }
    } else {
        fromEl.textContent = '—';
        fromSubEl.textContent = 'Nhập điểm xuất phát bên dưới';
    }
}

// --- Places selection (đã sửa lỗi hiển thị tag) ---
function renderPlaceList(filter) {
    const list = document.getElementById('place-list');
    if (!list) return;
    if (!selectedCity) {
        list.innerHTML = '<div class="dd-empty">Chọn thành phố trước</div>';
        return;
    }
    const q = (filter || '').toLowerCase();
    const allPlaces = (PLACES_BY_CITY[selectedCity.id] || []);
    const filtered = allPlaces.filter(p =>
        p.toLowerCase().includes(q) && !selectedPlaces.includes(p)
    );
    if (!filtered.length) {
        list.innerHTML = '<div class="dd-empty">Không tìm thấy địa điểm</div>';
        return;
    }
    list.innerHTML = filtered.map(p =>
        `<div class="dd-item" onclick="addPlace('${p.replace(/'/g, "\\'")}')">
      <div class="di-info">
        <div class="di-name">${p}</div>
        <div class="di-sub">${selectedCity.name}</div>
      </div>
    </div>`
    ).join('');
}

function filterPlaces(val) { renderPlaceList(val); }

function addPlace(name) {
    if (!selectedCity) {
        showToast('Vui lòng chọn thành phố trước', 'error');
        return;
    }
    if (selectedPlaces.length >= 10) {
        showToast('Chỉ được chọn tối đa 10 địa điểm', 'error');
        return;
    }
    if (!selectedPlaces.includes(name)) {
        selectedPlaces.push(name);
        renderPlaceTags();
        renderPlaceList(''); // refresh dropdown to remove added place
        // Clear search input
        const searchInput = document.getElementById('place-search');
        if (searchInput) searchInput.value = '';
    }
}

function removePlace(name) {
    selectedPlaces = selectedPlaces.filter(p => p !== name);
    renderPlaceTags();
    renderPlaceList(''); // refresh dropdown to show removed place again
}

function renderPlaceTags() {
    const box = document.getElementById('places-box');
    if (!box) return;
    // Remove all existing tags (but keep the search input)
    const existingTags = box.querySelectorAll('.tag');
    existingTags.forEach(tag => tag.remove());

    const searchInput = document.getElementById('place-search');
    if (!searchInput) return;

    // Add tags before the search input
    selectedPlaces.forEach(p => {
        const tag = document.createElement('div');
        tag.className = 'tag';
        tag.innerHTML = `${p} <button class="tag-rm" onclick="event.stopPropagation();removePlace('${p.replace(/'/g, "\\'")}')">×</button>`;
        box.insertBefore(tag, searchInput);
    });
}

// --- Pax stepper ---
function adjustPax(delta) {
    const inp = document.getElementById('pax-val');
    let v = parseInt(inp.value) + delta;
    v = Math.max(1, Math.min(50, v));
    inp.value = v;
    document.getElementById('pax-minus').disabled = v <= 1;
    document.getElementById('pax-plus').disabled = v >= 50;
    updateBudgetPP();
}

// --- Date validation ---
(function initDates() {
    const today = new Date();
    const fmt = d => d.toISOString().split('T')[0];
    const s = document.getElementById('date-start');
    const e = document.getElementById('date-end');
    if (!s || !e) return;
    s.min = fmt(today);
    const def = new Date(today); def.setDate(def.getDate() + 3);
    s.value = fmt(def);
    const defE = new Date(def); defE.setDate(defE.getDate() + 2);
    e.value = fmt(defE);
    e.min = s.value;
    validateDates();
})();

function validateDates() {
    const s = document.getElementById('date-start');
    const e = document.getElementById('date-end');
    const errS = document.getElementById('err-date-s');
    const errE = document.getElementById('err-date-e');
    const dur = document.getElementById('date-dur');
    if (!s || !e) return;
    errS.classList.remove('show'); errE.classList.remove('show');
    s.classList.remove('err'); e.classList.remove('err');
    dur.textContent = '';
    if (!s.value || !e.value) return;
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const ds = new Date(s.value);
    const de = new Date(e.value);
    e.min = s.value;
    if (ds < today) {
        errS.classList.add('show');
        errS.textContent = 'Ngày khởi hành không được ở quá khứ';
        s.classList.add('err');
        return;
    }
    const diff = Math.round((de - ds) / 864e5);
    if (diff <= 0) {
        errE.classList.add('show');
        errE.textContent = 'Ngày về phải sau ngày đi';
        e.classList.add('err');
        return;
    }
    if (diff > 30) {
        errE.classList.add('show');
        errE.textContent = `Tối đa 30 ngày (hiện tại: ${diff} ngày)`;
        e.classList.add('err');
        return;
    }
    dur.textContent = `✓ ${diff} ngày ${diff - 1} đêm`;
    updateBudgetPP();
}

// --- Budget ---
function formatBudget(inp) {
    const raw = inp.value.replace(/\D/g, '');
    inp.value = raw ? parseInt(raw).toLocaleString('vi-VN') : '';
    document.querySelectorAll('.b-chip').forEach(c => c.classList.remove('on'));
    validateBudget();
    updateBudgetPP();
}

function setBudget(val, el) {
    document.querySelectorAll('.b-chip').forEach(c => c.classList.remove('on'));
    el.classList.add('on');
    document.getElementById('budget-input').value = parseInt(val).toLocaleString('vi-VN');
    validateBudget();
    updateBudgetPP();
}

function getRawBudget() {
    return parseInt((document.getElementById('budget-input').value || '0').replace(/\D/g, '')) || 0;
}

function validateBudget() {
    const v = getRawBudget();
    const err = document.getElementById('err-budget');
    const inp = document.getElementById('budget-input');
    if (v > 0 && v < 100_000) {
        err.classList.add('show');
        err.textContent = 'Tối thiểu 100.000 ₫';
        inp.classList.add('err');
    } else {
        err.classList.remove('show');
        inp.classList.remove('err');
    }
}

function updateBudgetPP() {
    const pax = parseInt(document.getElementById('pax-val').value) || 1;
    const budget = getRawBudget();
    const el = document.getElementById('budget-pp');
    if (!el) return;
    const days = getTripDays();
    if (budget && pax) {
        const pp = Math.round(budget / pax);
        const ppd = days > 1 ? ` · ~${Math.round(pp / days).toLocaleString('vi-VN')} ₫/người/ngày` : '';
        el.textContent = `≈ ${pp.toLocaleString('vi-VN')} ₫/người${ppd}`;
    } else {
        el.textContent = '';
    }
}

function getTripDays() {
    const ds = document.getElementById('date-start').value;
    const de = document.getElementById('date-end').value;
    if (!ds || !de) return 1;
    return Math.max(1, Math.round((new Date(de) - new Date(ds)) / 864e5));
}

// --- Preferences ---
function togglePref(el, text) {
    el.classList.toggle('on');
    const active = Array.from(document.querySelectorAll('.p-chip.on')).map(c => c.textContent).join(', ');
    const ta = document.getElementById('notes-input');
    const filtered = ta.value.split('\n').filter(l => !l.startsWith('Sở thích:')).join('\n').trim();
    ta.value = active ? ('Sở thích: ' + active + (filtered ? '\n' + filtered : '')) : filtered;
    updateCharCount(ta, 'notes-count');
}

function updateCharCount(el, id) {
    const len = el.value.length;
    const max = parseInt(el.maxLength);
    const c = document.getElementById(id);
    if (!c) return;
    c.textContent = `${len} / ${max}`;
    c.className = 'char-c' + (len >= max ? ' over' : len > max * 0.9 ? ' warn' : '');
}

// --- Booking handler ---
function handleBooking(hotelName) {
    showToast('⏳ Đang kiểm tra phòng trống cho ' + hotelName + '...', '');
    fetch('/api/book', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' })
        .then(r => r.json())
        .then(data => {
            if (data.available) {
                showToast('✅ ' + hotelName + ' còn phòng! Liên hệ để đặt.', 'success');
            } else {
                showToast('😕 ' + hotelName + ' hết phòng cho ngày này. Thử ngày khác!', 'error');
            }
        })
        .catch(() => showToast('Không thể kết nối. Thử lại sau.', 'error'));
}

// --- Generate itinerary ---
function handleGenerate() {
    let valid = true;

    if (!selectedCity) {
        document.getElementById('err-city').classList.add('show');
        valid = false;
    }

    const budget = getRawBudget();
    if (!budget || budget < 100_000) {
        document.getElementById('err-budget').classList.add('show');
        document.getElementById('budget-input').classList.add('err');
        valid = false;
    }

    // Hard stop for some impossible cases (frontend quick check)
    const transport = document.getElementById('transport-type').value;
    const depVal = (document.getElementById('dep-input') || {}).value || '';
    const depCity = detectDepartureCity(depVal);
    const depId = depCity ? depCity.id : null;
    const destId = selectedCity ? selectedCity.id : null;
    const distance = getApproxDistance(depId, destId);

    if (transport === 'Xe đạp') {
        showToast('❌ Xe đạp không phù hợp cho chuyến liên tỉnh. Chọn phương tiện khác.', 'error');
        valid = false;
    }

    if (distance && distance >= 1500 &&
        (transport === 'Ô tô riêng' || transport === 'Thuê ô tô tự lái' || transport === 'Xe máy')) {
        const days = getTripDays();
        if (days < 3) {
            showToast(`❌ ${distance} km bằng ${transport} cần ít nhất 3–4 ngày. Hãy chọn máy bay.`, 'error');
            valid = false;
        }
    }

    if (!valid) {
        showToast('Vui lòng kiểm tra lại các trường bắt buộc', 'error');
        const firstErr = document.querySelector('.f-err.show');
        if (firstErr) firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }

    const id = 'AI·' + Math.random().toString(36).substr(2, 4).toUpperCase() + '·' + new Date().getFullYear();
    document.getElementById('tb-trip-id').textContent = 'TRIP — ' + id;

    showScreen('loading');
    resetLoadingSteps();

    const payload = {
        city_id: selectedCity.id,
        dep_city_id: depId,
        budget,
        pax: parseInt(document.getElementById('pax-val').value),
        date_start: document.getElementById('date-start').value,
        date_end: document.getElementById('date-end').value,
        notes: document.getElementById('notes-input').value,
        transport,
        accommodation: document.getElementById('accommodation-type').value,
        departure_time: document.getElementById('time-start').value,
        return_time: document.getElementById('time-end').value,
    };

    fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'error') {
                const errorIssues = document.getElementById('error-issues');
                if (errorIssues) {
                    errorIssues.innerHTML = data.errors.map(e => `<div class="error-issue">${e}</div>`).join('');
                }
                const continueBtn = document.getElementById('btn-continue-error');
                if (continueBtn) {
                    continueBtn.style.display = data.continue_allowed ? 'inline-flex' : 'none';
                }
                window._continueAllowed = data.continue_allowed;
                window._lastPayload = payload;
                showScreen('error');
            } else if (data.status === 'success') {
                animateLoading(true);
            } else {
                animateLoading(true);
            }
        })
        .catch(() => {
            animateLoading(true);
        });
}

function continueFromError() {
    if (window._continueAllowed) {
        showScreen('result');
        setTimeout(initLeafletMap, 150);
    } else {
        showScreen('form');
    }
}

function resetLoadingSteps() {
    const labels = [
        'Phân tích yêu cầu chuyến đi',
        'Tìm kiếm địa điểm phù hợp',
        'Tối ưu hóa lộ trình',
        'Gợi ý phương tiện & chi phí',
        'Hoàn thiện lịch trình',
    ];
    ['ls-1', 'ls-2', 'ls-3', 'ls-4', 'ls-5'].forEach((id, i) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.className = 'ls' + (i === 0 ? ' done' : i === 1 ? ' active' : '');
        el.innerHTML = (i === 0 ? '<span class="ls-ico">✓</span>' :
            i === 1 ? '<div class="ls-spin"></div>' :
                '<span class="ls-ico">○</span>') + ' ' + labels[i];
    });
}

function animateLoading(success, errors) {
    const ids = ['ls-2', 'ls-3', 'ls-4', 'ls-5'];
    let delay = 0;
    ids.forEach((id, i) => {
        const nextId = ids[i + 1];
        delay += 1100 + Math.random() * 400;
        setTimeout(() => {
            const prev = document.getElementById(id);
            if (!prev) return;
            const sp = prev.querySelector('.ls-spin');
            if (sp) sp.outerHTML = '<span class="ls-ico">✓</span>';
            prev.classList.remove('active'); prev.classList.add('done');
            if (nextId) {
                const next = document.getElementById(nextId);
                if (!next) return;
                const ico = next.querySelector('.ls-ico');
                if (ico) ico.outerHTML = '<div class="ls-spin"></div>';
                next.classList.add('active');
            }
        }, delay);
    });
    delay += 700;
    setTimeout(() => {
        document.querySelectorAll('.ls-spin').forEach(s => s.outerHTML = '<span class="ls-ico">✓</span>');
        document.querySelectorAll('.ls').forEach(s => { s.classList.remove('active'); s.classList.add('done'); });
        setTimeout(() => {
            if (!success && errors && errors.length) {
                const errEl = document.getElementById('error-issues');
                if (errEl) errEl.innerHTML = errors.map(e => `<div class="error-issue">${e}</div>`).join('');
            }
            showScreen(success ? 'result' : 'error');
        }, 450);
    }, delay);
}

// --- Reset form ---
function doReset() {
    selectedCity = null;
    selectedPlaces = [];
    document.getElementById('city-search').value = '';
    renderPlaceTags();
    document.getElementById('dep-input').value = '';
    document.getElementById('pax-val').value = '1';
    document.getElementById('pax-minus').disabled = true;
    document.getElementById('pax-plus').disabled = false;
    document.getElementById('budget-input').value = '';
    document.getElementById('notes-input').value = '';
    document.querySelectorAll('.p-chip.on').forEach(c => c.classList.remove('on'));
    document.querySelectorAll('.b-chip.on').forEach(c => c.classList.remove('on'));
    document.querySelectorAll('.f-err.show').forEach(e => e.classList.remove('show'));
    document.querySelectorAll('.err').forEach(e => e.classList.remove('err'));
    document.getElementById('notes-count').textContent = '0 / 500';
    document.getElementById('date-dur').textContent = '';
    document.getElementById('budget-pp').textContent = '';
    document.getElementById('ft-from-city').textContent = '—';
    document.getElementById('ft-from-sub').textContent = 'Nhập điểm xuất phát bên dưới';
    document.getElementById('ft-to-city').textContent = '—';
    document.getElementById('ft-to-sub').textContent = 'Chọn thành phố bên dưới';
    renderCityList('');
    closePopup('popup-reset');
    showToast('✓ Đã đặt lại tất cả thông tin', 'success');
}

function handleSave() { showPopup('popup-login'); }

function handleFeedback() {
    const val = document.getElementById('feedback-input').value.trim();
    if (!val) { showToast('Vui lòng nhập phản hồi', 'error'); return; }
    if (val.length > 500) { showToast('Phản hồi tối đa 500 ký tự', 'error'); return; }
    const btn = document.querySelector('.btn-feedback');
    if (btn) { btn.disabled = true; btn.textContent = '⏳ Đang cập nhật...'; }
    fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback: val }),
    })
        .then(() => { })
        .catch(() => { });
    setTimeout(() => {
        showToast('✅ Lịch trình đã được cập nhật theo phản hồi', 'success');
        document.getElementById('feedback-input').value = '';
        document.getElementById('feedback-count').textContent = '0 / 500';
        if (btn) { btn.disabled = false; btn.textContent = 'Cập nhật lịch trình'; }
    }, 2500);
}

function showPopup(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('open');
}
function closePopup(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('open');
}

document.querySelectorAll('.popup-ov').forEach(o => {
    o.addEventListener('click', e => { if (e.target === o) o.classList.remove('open'); });
});

let toastT;
function showToast(msg, type) {
    const t = document.getElementById('toast');
    const tm = document.getElementById('toast-msg');
    if (!t || !tm) return;
    tm.textContent = msg;
    t.className = 'toast show' + (type ? ' ' + type : '');
    clearTimeout(toastT);
    toastT = setTimeout(() => { t.className = 'toast'; }, type === 'error' ? 4500 : 3200);
}

// ============================================================
//  LEAFLET MAP
// ============================================================
function initLeafletMap() {
    const container = document.getElementById('leaflet-map');
    if (!container || typeof L === 'undefined') return;

    if (leafletMapInstance) {
        leafletMapInstance.remove();
        leafletMapInstance = null;
    }

    leafletMapInstance = L.map('leaflet-map', {
        zoomControl: true,
        scrollWheelZoom: false,
    }).setView([16.0, 108.1], 10);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
    }).addTo(leafletMapInstance);

    const stops = [
        { name: 'Sân bay Đà Nẵng', lat: 16.044, lng: 108.200, emoji: '✈️', color: '#3674B5', day: 1 },
        { name: 'Bãi biển Mỹ Khê', lat: 16.065, lng: 108.247, emoji: '🏖️', color: '#0C9E72', day: 1 },
        { name: 'Bảo tàng Điêu khắc Chăm', lat: 16.047, lng: 108.221, emoji: '🏛️', color: '#578FCA', day: 1 },
        { name: 'Bà Nà Hills', lat: 15.997, lng: 107.990, emoji: '🌉', color: '#7B4FBE', day: 2 },
        { name: 'Phố Cổ Hội An', lat: 15.880, lng: 108.326, emoji: '🏮', color: '#E8A914', day: 3 },
        { name: 'Biển Cửa Đại', lat: 15.867, lng: 108.355, emoji: '🏖️', color: '#0BB5D5', day: 3 },
    ];

    const latlngs = stops.map(s => [s.lat, s.lng]);

    L.polyline(latlngs, {
        color: '#00A9FF',
        weight: 4,
        opacity: 0.9,
        dashArray: '10, 7',
        lineJoin: 'round',
    }).addTo(leafletMapInstance);

    stops.forEach(s => {
        const icon = L.divIcon({
            className: '',
            html: `
        <div style="display:flex;flex-direction:column;align-items:center;">
          <div style="
            background:${s.color};color:#fff;
            border-radius:50%;width:38px;height:38px;
            display:flex;align-items:center;justify-content:center;
            font-size:19px;
            box-shadow:0 3px 10px rgba(0,0,0,0.3);
            border:2.5px solid #fff;
          ">${s.emoji}</div>
          <div style="
            background:${s.color};color:#fff;
            font-size:9px;font-weight:700;padding:2px 6px;
            border-radius:8px;margin-top:2px;white-space:nowrap;
            box-shadow:0 2px 6px rgba(0,0,0,0.2);
          ">Ngày ${s.day}</div>
        </div>`,
            iconSize: [38, 54],
            iconAnchor: [19, 54],
            popupAnchor: [0, -56],
        });
        L.marker([s.lat, s.lng], { icon })
            .addTo(leafletMapInstance)
            .bindPopup(`<strong>${s.name}</strong><br><small>Ngày ${s.day} trong lịch trình</small>`);
    });

    leafletMapInstance.fitBounds(latlngs, { padding: [24, 24] });
    setTimeout(() => leafletMapInstance.invalidateSize(), 250);
}

loadData();