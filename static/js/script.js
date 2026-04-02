// Global data
let CITIES = [];
let PLACES_BY_CITY = {};

let selectedCity = null;
let selectedPlaces = [];

// Load data from API
async function loadData() {
    try {
        const [cr, pr] = await Promise.all([
            fetch('/api/cities').then(r => r.json()),
            fetch('/api/places').then(r => r.json())
        ]);
        CITIES = cr;
        PLACES_BY_CITY = pr;
    } catch (e) { }
    renderCityList('');
    document.getElementById('dep-input').value = 'Sân bay Nội Bài, Hà Nội';
    updateDeparture('Sân bay Nội Bài, Hà Nội');
}

// Screen handling
function showScreen(name) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('screen-' + name).classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Dropdowns
function openDrop(id) {
    document.getElementById(id).classList.add('open');
    if (id === 'dd-city') renderCityList('');
    if (id === 'dd-place') renderPlaceList('');
}
function closeDrop(id) { document.getElementById(id).classList.remove('open'); }
function toggleDrop(id) {
    const el = document.getElementById(id);
    el.classList.contains('open') ? closeDrop(id) : openDrop(id);
}

// City dropdown (single selection)
function renderCityList(filter) {
    const list = document.getElementById('city-list');
    const q = (filter || '').toLowerCase();
    const filtered = CITIES.filter(c => c.name.toLowerCase().includes(q) || c.sub.toLowerCase().includes(q));
    if (!filtered.length) { list.innerHTML = '<div class="dd-empty">Không tìm thấy thành phố</div>'; return; }
    list.innerHTML = filtered.map(c => {
        const isSel = selectedCity && selectedCity.id === c.id;
        return `<div class="dd-item ${isSel ? 'sel' : ''}" onclick="selectCity('${c.id}')">
      <img class="di-img" src="${c.img}" onerror="this.style.background='${c.color}';this.removeAttribute('src')" alt="${c.name}" style="background:${c.color}">
      <div class="di-info"><div class="di-name">${c.name}</div><div class="di-sub">${c.sub}</div></div>
      ${isSel ? '<span class="di-check">✓</span>' : ''}
    </div>`;
    }).join('');
}

function filterCities(val) { renderCityList(val); }

function selectCity(id) {
    const city = CITIES.find(c => c.id === id);
    if (!city) return;
    selectedCity = city;
    // Clear selected places because they belong to previous city
    selectedPlaces = [];
    renderPlaceTags();
    renderCityList(document.getElementById('city-search').value);
    // Update the dropdown input field with selected city name
    const searchInput = document.getElementById('city-search');
    searchInput.value = city.name;
    // Close dropdown after selection
    closeDrop('dd-city');
    updateFromToDisplay();
    document.getElementById('err-city').classList.remove('show');
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
    if (val.trim()) {
        const short = val.split(',')[0].trim().split(' ').slice(-2).join(' ');
        fromEl.textContent = short.length > 10 ? short.substring(0, 10) + '...' : short;
        fromSubEl.textContent = val;
    } else {
        fromEl.textContent = '—';
        fromSubEl.textContent = 'Nhập điểm xuất phát bên dưới';
    }
}

// Places selection
function renderPlaceList(filter) {
    const list = document.getElementById('place-list');
    if (!selectedCity) { list.innerHTML = '<div class="dd-empty">Chọn thành phố trước</div>'; return; }
    const q = (filter || '').toLowerCase();
    const allPlaces = (PLACES_BY_CITY[selectedCity.id] || []).map(p => ({ name: p, city: selectedCity.name }));
    const filtered = allPlaces.filter(p => p.name.toLowerCase().includes(q) && !selectedPlaces.includes(p.name));
    if (!filtered.length) { list.innerHTML = '<div class="dd-empty">Không tìm thấy địa điểm</div>'; return; }
    list.innerHTML = filtered.map(p =>
        `<div class="dd-item" onclick="addPlace('${p.name.replace(/'/g, "\\'")}')">
      <div class="di-info"><div class="di-name">${p.name}</div><div class="di-sub">${p.city}</div></div>
    </div>`
    ).join('');
}

function filterPlaces(val) { renderPlaceList(val); }

function addPlace(name) {
    if (selectedPlaces.length >= 10) {
        showToast('Chỉ được chọn tối đa 10 địa điểm', 'error');
        return;
    }
    if (!selectedPlaces.includes(name)) {
        selectedPlaces.push(name);
        renderPlaceTags();
        renderPlaceList('');
        document.getElementById('place-search').value = '';
    }
}

function removePlace(name) {
    selectedPlaces = selectedPlaces.filter(p => p !== name);
    renderPlaceTags();
    renderPlaceList('');
}

function renderPlaceTags() {
    const box = document.getElementById('places-box');
    box.querySelectorAll('.tag').forEach(t => t.remove());
    const search = document.getElementById('place-search');
    selectedPlaces.forEach(p => {
        const tag = document.createElement('div');
        tag.className = 'tag';
        tag.innerHTML = `${p} <button class="tag-rm" onclick="event.stopPropagation();removePlace('${p.replace(/'/g, "\\'")}')">×</button>`;
        box.insertBefore(tag, search);
    });
}

// Pax stepper
function adjustPax(delta) {
    const inp = document.getElementById('pax-val');
    let v = parseInt(inp.value) + delta;
    v = Math.max(1, Math.min(50, v));
    inp.value = v;
    document.getElementById('pax-minus').disabled = v <= 1;
    document.getElementById('pax-plus').disabled = v >= 50;
    updateBudgetPP();
}

// Date handling
(function initDates() {
    const today = new Date();
    const fmt = d => d.toISOString().split('T')[0];
    const s = document.getElementById('date-start');
    const e = document.getElementById('date-end');
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
    errS.classList.remove('show'); errE.classList.remove('show');
    s.classList.remove('err'); e.classList.remove('err');
    dur.textContent = '';
    if (!s.value || !e.value) return;
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const ds = new Date(s.value);
    const de = new Date(e.value);
    e.min = s.value;
    if (ds < today) { errS.classList.add('show'); errS.textContent = 'Ngày khởi hành không được ở quá khứ'; s.classList.add('err'); return; }
    const diff = Math.round((de - ds) / 864e5);
    if (diff <= 0) { errE.classList.add('show'); errE.textContent = 'Ngày về phải sau ngày đi'; e.classList.add('err'); return; }
    if (diff > 30) { errE.classList.add('show'); errE.textContent = `Tối đa 30 ngày (hiện tại: ${diff} ngày)`; e.classList.add('err'); return; }
    dur.textContent = `✓ ${diff} ngày ${diff - 1} đêm`;
    updateBudgetPP();
}

// Budget
function formatBudget(inp) {
    const raw = inp.value.replace(/\D/g, '');
    inp.value = raw ? parseInt(raw).toLocaleString('vi-VN') : '';
    document.querySelectorAll('.b-chip').forEach(c => c.classList.remove('on'));
    validateBudget(); updateBudgetPP();
}

function setBudget(val, el) {
    document.querySelectorAll('.b-chip').forEach(c => c.classList.remove('on'));
    el.classList.add('on');
    document.getElementById('budget-input').value = parseInt(val).toLocaleString('vi-VN');
    validateBudget(); updateBudgetPP();
}

function getRawBudget() { return parseInt((document.getElementById('budget-input').value || '0').replace(/\D/g, '')) || 0; }

function validateBudget() {
    const v = getRawBudget();
    const err = document.getElementById('err-budget');
    const inp = document.getElementById('budget-input');
    if (v > 0 && v < 100000) { err.classList.add('show'); inp.classList.add('err'); }
    else { err.classList.remove('show'); inp.classList.remove('err'); }
}

function updateBudgetPP() {
    const pax = parseInt(document.getElementById('pax-val').value) || 1;
    const budget = getRawBudget();
    const el = document.getElementById('budget-pp');
    el.textContent = (budget && pax > 1) ? `≈ ${Math.round(budget / pax).toLocaleString('vi-VN')} ₫ / người` : '';
}

// Preferences
function togglePref(el, text) {
    el.classList.toggle('on');
    const active = Array.from(document.querySelectorAll('.p-chip.on')).map(c => c.textContent).join(', ');
    const ta = document.getElementById('notes-input');
    const lines = ta.value.split('\n');
    const filtered = lines.filter(l => !l.startsWith('Sở thích:')).join('\n').trim();
    let newValue = '';
    if (active) {
        newValue = 'Sở thích: ' + active;
        if (filtered) newValue += '\n' + filtered;
    } else {
        newValue = filtered;
    }
    ta.value = newValue;
    updateCharCount(ta, 'notes-count');
}

function updateCharCount(el, id) {
    const len = el.value.length;
    const max = parseInt(el.maxLength);
    const c = document.getElementById(id);
    c.textContent = `${len} / ${max}`;
    c.className = 'char-c' + (len >= max ? ' over' : len > max * .9 ? ' warn' : '');
}

// Generate itinerary
function handleGenerate() {
    let valid = true;
    if (!selectedCity) { document.getElementById('err-city').classList.add('show'); valid = false; }
    const budget = getRawBudget();
    if (!budget || budget < 10000) {
        document.getElementById('err-budget').classList.add('show');
        document.getElementById('budget-input').classList.add('err');
        valid = false;
    }
    if (!valid) { showToast('Vui lòng điền đủ các trường bắt buộc', 'error'); return; }
    const id = 'AI·' + Math.random().toString(36).substr(2, 4).toUpperCase() + '·' + new Date().getFullYear();
    document.getElementById('tb-trip-id').textContent = 'TRIP — ' + id;
    showScreen('loading');
    resetLoadingSteps();

    const payload = {
        city_id: selectedCity ? selectedCity.id : null,
        budget: budget,
        pax: parseInt(document.getElementById('pax-val').value),
        date_start: document.getElementById('date-start').value,
        date_end: document.getElementById('date-end').value,
        notes: document.getElementById('notes-input').value,
        transport: document.getElementById('transport-type').value,
        accommodation: document.getElementById('accommodation-type').value,
        departure_time: document.getElementById('time-start').value,
        return_time: document.getElementById('time-end').value
    };

    fetch('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
        .then(r => r.json())
        .then(data => { animateLoading(data.status === 'success'); })
        .catch(() => { animateLoading(true); });
}

function resetLoadingSteps() {
    const labels = ['Phân tích yêu cầu chuyến đi', 'Tìm kiếm địa điểm phù hợp', 'Tối ưu hóa lộ trình', 'Gợi ý phương tiện & chi phí', 'Hoàn thiện lịch trình'];
    ['ls-1', 'ls-2', 'ls-3', 'ls-4', 'ls-5'].forEach((id, i) => {
        const el = document.getElementById(id);
        el.className = 'ls' + (i === 0 ? ' done' : i === 1 ? ' active' : '');
        el.innerHTML = (i === 0 ? '<span class="ls-ico">✓</span>' : i === 1 ? '<div class="ls-spin"></div>' : '<span class="ls-ico">○</span>') + ' ' + labels[i];
    });
}

function animateLoading(success) {
    const ids = ['ls-2', 'ls-3', 'ls-4', 'ls-5'];
    let delay = 0;
    ids.forEach((id, i) => {
        const nextId = ids[i + 1];
        delay += 1100 + Math.random() * 400;
        setTimeout(() => {
            const prev = document.getElementById(id);
            const sp = prev.querySelector('.ls-spin');
            if (sp) sp.outerHTML = '<span class="ls-ico">✓</span>';
            prev.classList.remove('active'); prev.classList.add('done');
            if (nextId) {
                const next = document.getElementById(nextId);
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
        setTimeout(() => showScreen(success ? 'result' : 'error'), 450);
    }, delay);
}

// Reset
function doReset() {
    selectedCity = null;
    selectedPlaces = [];
    document.getElementById('city-search').value = '';
    document.getElementById('city-trigger').querySelectorAll('.tag').forEach(t => t.remove());
    document.getElementById('places-box').querySelectorAll('.tag').forEach(t => t.remove());
    document.getElementById('dep-input').value = '';
    document.getElementById('pax-val').value = '1';
    document.getElementById('pax-minus').disabled = true;
    document.getElementById('pax-plus').disabled = false;
    document.getElementById('budget-input').value = '';
    document.getElementById('notes-input').value = '';
    document.querySelectorAll('.p-chip.on').forEach(c => c.classList.remove('on'));
    document.querySelectorAll('.b-chip.on').forEach(c => c.classList.remove('on'));
    document.querySelectorAll('.f-err.show').forEach(e => e.classList.remove('show'));
    document.querySelectorAll('.text-input.err,.stub-date.err,.budget-input.err,.dd-trigger.err').forEach(e => e.classList.remove('err'));
    document.getElementById('notes-count').textContent = '0 / 500';
    document.getElementById('date-dur').textContent = '';
    document.getElementById('budget-pp').textContent = '';
    document.getElementById('ft-from-city').textContent = '—';
    document.getElementById('ft-from-sub').textContent = 'Nhập điểm xuất phát bên dưới';
    document.getElementById('ft-to-city').textContent = '—';
    document.getElementById('ft-to-sub').textContent = 'Chọn thành phố bên dưới';
    renderCityList('');
    closePopup('popup-reset');
    showToast('Đã đặt lại tất cả thông tin');
}

// Save (login required)
function handleSave() { showPopup('popup-login'); }

// Feedback
function handleFeedback() {
    const val = document.getElementById('feedback-input').value.trim();
    if (!val) { showToast('Vui lòng nhập phản hồi', 'error'); return; }
    showToast('AI đang cập nhật lịch trình...');
    fetch('/api/feedback', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ feedback: val }) })
        .then(() => { })
        .catch(() => { });
    setTimeout(() => {
        showToast('Lịch trình đã được cập nhật theo phản hồi', 'success');
        document.getElementById('feedback-input').value = '';
        document.getElementById('feedback-count').textContent = '0 / 500';
    }, 2500);
}

// Popups & Toast
function showPopup(id) { document.getElementById(id).classList.add('open'); }
function closePopup(id) { document.getElementById(id).classList.remove('open'); }

document.querySelectorAll('.popup-ov').forEach(o => {
    o.addEventListener('click', e => { if (e.target === o) o.classList.remove('open'); });
});

let toastT;
function showToast(msg, type) {
    const t = document.getElementById('toast');
    document.getElementById('toast-msg').textContent = msg;
    t.className = 'toast show' + (type ? ' ' + type : '');
    clearTimeout(toastT);
    toastT = setTimeout(() => t.className = 'toast', 3200);
}

// Initialize
loadData();