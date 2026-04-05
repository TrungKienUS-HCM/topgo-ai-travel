import random
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory

app = Flask(__name__)

# --- Static city data ---
CITIES_DATA = [
    {
        "id": "dn",
        "name": "Đà Nẵng",
        "abbr": "DAD",
        "sub": "Miền Trung",
        "img": "/static/img/cities/da-nang.jpg",
        "color": "#3674B5",
    },
    {
        "id": "ha",
        "name": "Hà Nội",
        "abbr": "HAN",
        "sub": "Miền Bắc",
        "img": "/static/img/cities/ha-noi.png",
        "color": "#578FCA",
    },
    {
        "id": "hcm",
        "name": "TP. Hồ Chí Minh",
        "abbr": "SGN",
        "sub": "Miền Nam",
        "img": "/static/img/cities/hcm.jpg",
        "color": "#0C9E72",
    },
    {
        "id": "hoian",
        "name": "Hội An",
        "abbr": "HOI",
        "sub": "Quảng Nam",
        "img": "/static/img/cities/hoi-an.jpg",
        "color": "#E8A914",
    },
    {
        "id": "nt",
        "name": "Nha Trang",
        "abbr": "CXR",
        "sub": "Khánh Hòa",
        "img": "/static/img/cities/nha-trang.jpg",
        "color": "#0BB5D5",
    },
    {
        "id": "dl",
        "name": "Đà Lạt",
        "abbr": "DLI",
        "sub": "Lâm Đồng",
        "img": "/static/img/cities/da-lat.jpg",
        "color": "#7B4FBE",
    },
    {
        "id": "ph",
        "name": "Phú Quốc",
        "abbr": "PQC",
        "sub": "Kiên Giang",
        "img": "/static/img/cities/phu-quoc.jpg",
        "color": "#1CB869",
    },
    {
        "id": "hue",
        "name": "Huế",
        "abbr": "HUI",
        "sub": "TT. Huế",
        "img": "/static/img/cities/hue.jpg",
        "color": "#C0392B",
    },
    {
        "id": "qni",
        "name": "Quy Nhơn",
        "abbr": "UIH",
        "sub": "Bình Định",
        "img": "/static/img/cities/quy-nhon.jpg",
        "color": "#E67E22",
    },
    {
        "id": "hl",
        "name": "Hạ Long",
        "abbr": "HPH",
        "sub": "Quảng Ninh",
        "img": "/static/img/cities/ha-long.jpg",
        "color": "#2980B9",
    },
]

PLACES_DATA = {
    "dn": [
        "Bãi biển Mỹ Khê",
        "Cầu Rồng",
        "Bà Nà Hills",
        "Núi Sơn Trà",
        "Bảo tàng Điêu khắc Chăm",
        "Cầu Vàng",
        "Bán đảo Sơn Trà",
        "Phố đêm Đà Nẵng",
        "Nhà thờ Chính tòa Đà Nẵng",
        "Công viên Châu Á",
    ],
    "hoian": [
        "Phố Cổ Hội An",
        "Chùa Cầu",
        "Làng rau Trà Quế",
        "Biển Cửa Đại",
        "Làng gốm Thanh Hà",
        "Mỳ Cao Lầu",
        "Đảo Cù Lao Chàm",
        "Hội quán Phúc Kiến",
        "Nhà cổ Tấn Ký",
        "Chợ đêm Hội An",
    ],
    "ha": [
        "Hồ Hoàn Kiếm",
        "Lăng Chủ tịch Hồ Chí Minh",
        "Văn Miếu – Quốc Tử Giám",
        "Phố cổ 36 phố phường",
        "Hồ Tây",
        "Chùa Một Cột",
        "Hoàng Thành Thăng Long",
        "Nhà thờ Lớn Hà Nội",
        "Bảo tàng Dân tộc học",
        "Cầu Long Biên",
    ],
    "hcm": [
        "Nhà thờ Đức Bà",
        "Địa đạo Củ Chi",
        "Chợ Bến Thành",
        "Bảo tàng Chứng tích Chiến tranh",
        "Dinh Độc Lập",
        "Phố đi bộ Nguyễn Huệ",
        "Bến Nhà Rồng",
        "Chùa Vĩnh Nghiêm",
        "Suối Tiên",
        "Bảo tàng Mỹ thuật TP.HCM",
    ],
    "nt": [
        "Tháp Bà Ponagar",
        "Vinpearl Land",
        "Vịnh Nha Trang",
        "Đảo Hòn Mun",
        "Chùa Long Sơn",
        "Biển Bãi Dài",
        "Hòn Chồng",
        "Suối khoáng nóng Tháp Bà",
        "Nhà thờ Núi",
        "Viện Hải dương học",
    ],
    "dl": [
        "Hồ Xuân Hương",
        "Thung lũng Tình Yêu",
        "Đỉnh LangBiang",
        "Làng hoa Vạn Thành",
        "Làng Cù Lần",
        "Dinh Bảo Đại",
        "Nhà thờ Con Gà",
        "Vườn hoa Đà Lạt",
        "Thác Pongour",
        "Ga Đà Lạt",
    ],
    "ph": [
        "Grand World Phú Quốc",
        "Bãi Sao",
        "Cáp treo Hòn Thơm",
        "Vinpearl Safari",
        "Chợ đêm Phú Quốc",
        "Bãi Dài",
        "Nhà tù Phú Quốc",
        "Mũi Điện",
        "Suối Tranh",
        "Hòn Một",
    ],
    "hue": [
        "Đại Nội – Hoàng Thành Huế",
        "Lăng Tự Đức",
        "Chùa Thiên Mụ",
        "Lăng Khải Định",
        "Cầu Trường Tiền",
        "Chợ Đông Ba",
        "Lăng Minh Mạng",
        "Đồi Vọng Cảnh",
        "Sông Hương",
        "Chùa Từ Đàm",
    ],
    "qni": [
        "Ghềnh Ráng Tiên Sa",
        "Eo Gió",
        "Kỳ Co",
        "Thành Hoàng Đế",
        "Bãi biển Quy Nhơn",
        "Bãi Xép",
        "Chùa Thập Tháp",
        "Đảo Hòn Khô",
        "Cầu Thị Nại",
        "Bảo tàng Quang Trung",
    ],
    "hl": [
        "Vịnh Hạ Long",
        "Hang Sửng Sốt",
        "Đảo Ti Tốp",
        "Làng chài Cửa Vạn",
        "Đảo Cát Bà",
        "Núi Bài Thơ",
        "Động Thiên Cung",
        "Hang Đầu Gỗ",
        "Bảo tàng Quảng Ninh",
        "Chợ đêm Hạ Long",
    ],
}

# Approximate road distances between cities (km)
CITY_DISTANCES = {
    ("ha", "hcm"): 1700,
    ("hcm", "ha"): 1700,
    ("ha", "dn"): 764,
    ("dn", "ha"): 764,
    ("ha", "hue"): 666,
    ("hue", "ha"): 666,
    ("ha", "hoian"): 773,
    ("hoian", "ha"): 773,
    ("ha", "nt"): 1278,
    ("nt", "ha"): 1278,
    ("ha", "dl"): 1480,
    ("dl", "ha"): 1480,
    ("ha", "ph"): 2050,
    ("ph", "ha"): 2050,
    ("ha", "hl"): 165,
    ("hl", "ha"): 165,
    ("ha", "qni"): 1070,
    ("qni", "ha"): 1070,
    ("hcm", "dn"): 964,
    ("dn", "hcm"): 964,
    ("hcm", "hue"): 1045,
    ("hue", "hcm"): 1045,
    ("hcm", "hoian"): 970,
    ("hoian", "hcm"): 970,
    ("hcm", "nt"): 448,
    ("nt", "hcm"): 448,
    ("hcm", "dl"): 308,
    ("dl", "hcm"): 308,
    ("hcm", "ph"): 460,
    ("ph", "hcm"): 460,
    ("hcm", "qni"): 690,
    ("qni", "hcm"): 690,
    ("dn", "hue"): 100,
    ("hue", "dn"): 100,
    ("dn", "hoian"): 30,
    ("hoian", "dn"): 30,
    ("dn", "nt"): 534,
    ("nt", "dn"): 534,
    ("dn", "dl"): 420,
    ("dl", "dn"): 420,
}

# Minimum budget per person for each transport type (one-way)
TRANSPORT_MIN_PER_PAX = {
    "Máy bay": 700_000,
    "Tàu hỏa": 200_000,
    "Xe khách": 150_000,
    "Ô tô riêng": 0,
    "Thuê ô tô tự lái": 400_000,
    "Xe máy": 0,
    "Xe đạp": 0,
}

# BỔ SUNG: Chi phí theo km cho tàu hỏa và xe khách (để tính toán chi phí thực tế)
TRAIN_COST_PER_KM = 1000  # VND/km/người
BUS_COST_PER_KM = 800  # VND/km/người

# BỔ SUNG: Vận tốc trung bình (km/h) để ước lượng thời gian di chuyển
AVG_SPEED = {
    "Máy bay": 800,
    "Tàu hỏa": 60,
    "Xe khách": 50,
    "Ô tô riêng": 60,
    "Thuê ô tô tự lái": 60,
    "Xe máy": 40,
    "Xe đạp": 15,
}

# Suggested minimum budget per night per room for accommodation types
ACCOMMODATION_MIN_PER_NIGHT = {
    "Resort": 1_200_000,
    "Villa": 1_500_000,
    "Khách sạn": 400_000,
    "Homestay": 250_000,
    "Airbnb": 350_000,
    "Căn hộ": 300_000,
}


# ========== HÀM HỖ TRỢ TÍNH TOÁN ==========
def get_min_transport_cost(dep_id, dest_id, transport, pax):
    """Tính chi phí di chuyển tối thiểu cho cả đoàn (khứ hồi nếu là máy bay)."""
    if not dep_id or not dest_id or dep_id == dest_id:
        return 0
    distance = CITY_DISTANCES.get((dep_id, dest_id))
    if distance is None:
        return 0

    if transport == "Máy bay":
        return pax * TRANSPORT_MIN_PER_PAX["Máy bay"] * 2
    elif transport == "Tàu hỏa":
        return pax * distance * TRAIN_COST_PER_KM
    elif transport == "Xe khách":
        return pax * distance * BUS_COST_PER_KM
    elif transport == "Thuê ô tô tự lái":
        # Sẽ tính riêng theo ngày trong hàm khác
        return 0
    else:
        return 0


def get_min_accommodation_cost(accommodation, pax, days):
    """Tính chi phí lưu trú tối thiểu cho toàn bộ chuyến đi."""
    if not accommodation:
        return 0
    min_per_night = ACCOMMODATION_MIN_PER_NIGHT.get(accommodation, 200_000)
    rooms_needed = (pax + 1) // 2
    return min_per_night * rooms_needed * days


def get_travel_hours(dep_id, dest_id, transport):
    """Ước lượng số giờ di chuyển một chiều."""
    if not dep_id or not dest_id or dep_id == dest_id:
        return 0
    distance = CITY_DISTANCES.get((dep_id, dest_id))
    if distance is None:
        return 0
    speed = AVG_SPEED.get(transport, 50)
    return distance / speed


# ========== CÁC HÀM KIỂM TRA ==========
def validate_transport(dep_id, dest_id, transport, days, pax, budget):
    """Trả về list các tuple (loại, thông báo) với loại = 'error' hoặc 'warning'."""
    result = []
    if not dep_id or not dest_id:
        return result

    distance = CITY_DISTANCES.get((dep_id, dest_id))
    if distance is None:
        return result

    # 1. Xe đạp chỉ cho phép khi cùng tỉnh (không có dep_id hoặc dep_id == dest_id)
    if transport == "Xe đạp":
        if dep_id != dest_id:
            result.append(
                (
                    "error",
                    "Xe đạp chỉ phù hợp khi di chuyển trong cùng một thành phố/tỉnh. Vui lòng chọn phương tiện khác cho chuyến đi liên tỉnh.",
                )
            )
        return result

    # 2. Kiểm tra thời gian di chuyển so với số ngày
    travel_hours = get_travel_hours(dep_id, dest_id, transport)
    max_hours_per_day = 12  # giả sử mỗi ngày chỉ đi 12 giờ tối đa
    if days == 1 and travel_hours > max_hours_per_day:
        result.append(
            (
                "error",
                f"⏱ Thời gian di chuyển một chiều ước tính {travel_hours:.1f} giờ, vượt quá {max_hours_per_day} giờ/ngày. Không thể thực hiện trong 1 ngày.",
            )
        )
    elif travel_hours > days * max_hours_per_day:
        result.append(
            (
                "error",
                f"⏱ Tổng thời gian di chuyển {travel_hours:.1f} giờ cần ít nhất {int(travel_hours / max_hours_per_day) + 1} ngày. Hiện tại chỉ có {days} ngày.",
            )
        )

    # 3. Các cảnh báo mềm về quãng đường
    if transport == "Xe máy":
        if distance > 800:
            result.append(
                (
                    "error",
                    f"Xe máy không phù hợp cho quãng đường {distance} km. Hãy chọn xe khách, tàu hỏa hoặc máy bay.",
                )
            )
        elif distance > 500:
            result.append(
                (
                    "warning",
                    f"⚠️ Quãng đường {distance} km bằng xe máy rất vất vả và nguy hiểm. Cân nhắc phương tiện khác.",
                )
            )
    if transport == "Xe khách" and distance > 800:
        result.append(
            (
                "warning",
                f"⚠️ Xe khách cho {distance} km sẽ mất 15–20 tiếng. Hãy cân nhắc tàu hỏa hoặc máy bay.",
            )
        )
    if transport in ("Ô tô riêng", "Thuê ô tô tự lái"):
        if distance >= 1500 and days < 3:
            result.append(
                (
                    "error",
                    f"❌ Quãng đường {distance} km bằng ô tô cần ít nhất 3–4 ngày (hiện tại: {days} ngày). Đề xuất chọn máy bay.",
                )
            )
        elif distance > 700 and days <= 1:
            result.append(
                (
                    "warning",
                    f"⚠️ Lái xe {distance} km mất 8–12 tiếng, không khả thi trong {days} ngày. Cân nhắc máy bay hoặc tàu.",
                )
            )

    # 4. Kiểm tra ngân sách cho từng phương tiện
    if transport == "Máy bay":
        min_flight = pax * TRANSPORT_MIN_PER_PAX["Máy bay"] * 2
        if budget < min_flight:
            result.append(
                (
                    "error",
                    f"💰 Ngân sách quá thấp cho vé máy bay khứ hồi. Cần tối thiểu ~{min_flight:,} ₫ cho {pax} người. (Hiện tại: {budget:,} ₫)",
                )
            )
    if transport == "Thuê ô tô tự lái":
        rental_cost = 500_000 * days
        if budget < rental_cost:
            result.append(
                (
                    "error",
                    f"💰 Ngân sách không đủ cho thuê xe tự lái {days} ngày (tối thiểu {rental_cost:,} ₫). Hãy chọn phương tiện khác hoặc tăng ngân sách.",
                )
            )

    # 5. BỔ SUNG: Kiểm tra chi phí tàu hỏa / xe khách dựa trên khoảng cách
    if transport == "Tàu hỏa":
        cost = pax * distance * TRAIN_COST_PER_KM
        if budget < cost:
            result.append(
                (
                    "error",
                    f"💰 Ngân sách không đủ cho vé tàu hỏa (ước tính {cost:,} ₫ cho {pax} người). Cần tăng ngân sách hoặc chọn phương tiện rẻ hơn.",
                )
            )
    if transport == "Xe khách":
        cost = pax * distance * BUS_COST_PER_KM
        if budget < cost:
            result.append(
                (
                    "error",
                    f"💰 Ngân sách không đủ cho vé xe khách (ước tính {cost:,} ₫ cho {pax} người). Cần tăng ngân sách hoặc chọn phương tiện rẻ hơn.",
                )
            )

    return result


def validate_accommodation(accommodation, budget, pax, days):
    """Kiểm tra ngân sách cho chỗ ở."""
    errors = []
    if not accommodation or not budget or not pax or not days:
        return errors
    min_per_night = ACCOMMODATION_MIN_PER_NIGHT.get(accommodation, 200_000)
    rooms_needed = (pax + 1) // 2
    total_min_accommodation = min_per_night * rooms_needed * days
    if budget < total_min_accommodation:
        errors.append(
            (
                "error",
                f"💰 Ngân sách không đủ cho loại hình {accommodation} với {pax} người trong {days} ngày. Cần tối thiểu ~{total_min_accommodation:,} ₫ cho chỗ ở (giả sử {rooms_needed} phòng).",
            )
        )
    return errors


# ========== DEMO: Giả lập giá thực tế không đủ ngân sách ==========
def simulate_actual_pricing_check(city_id, budget, pax, days):
    """
    DEMO: Hàm này giả lập việc tra cứu giá thực tế từ dataset (khách sạn, vé tham quan, ăn uống...)
    và phát hiện ngân sách không đủ. Trả về (có_lỗi, danh_sách_lỗi)
    Trong thực tế, sẽ gọi database hoặc API để tính tổng chi phí tối thiểu cho chuyến đi.
    """
    # Giả lập: nếu ngân sách dưới 500.000đ/người/ngày thì báo lỗi
    min_budget_per_person_per_day = 500_000
    required_budget = pax * days * min_budget_per_person_per_day
    if budget < required_budget:
        return True, [
            f"💰 Sau khi tra cứu giá thực tế, hệ thống ước tính cần tối thiểu {required_budget:,} ₫ cho {pax} người trong {days} ngày. Ngân sách của bạn ({budget:,} ₫) không đáp ứng được. Vui lòng tăng ngân sách hoặc giảm số ngày/số người."
        ]
    return False, []


# ========== FLASK ROUTES ==========
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)


@app.route("/api/cities")
def api_cities():
    return jsonify(CITIES_DATA)


@app.route("/api/places")
def api_places():
    return jsonify(PLACES_DATA)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json() or {}
    city_id = data.get("city_id")
    dep_city_id = data.get("dep_city_id")
    budget = data.get("budget", 0)
    pax = data.get("pax", 1)
    date_start = data.get("date_start", "")
    date_end = data.get("date_end", "")
    transport = data.get("transport", "")
    accommodation = data.get("accommodation", "")
    departure_time = data.get("departure_time", "07:00")
    return_time = data.get("return_time", "18:00")

    errors = []  # list of strings for display
    continue_allowed = True

    # ----- KIỂM TRA DỮ LIỆU ĐẦU VÀO -----
    # 1. Kiểm tra thành phố đích
    if not city_id:
        errors.append("📍 Chưa chọn thành phố muốn đến.")
        continue_allowed = False

    # 2. Kiểm tra ngân sách hợp lệ (số dương, không âm)
    if not isinstance(budget, (int, float)) or budget <= 0:
        errors.append("💰 Ngân sách phải là số dương lớn hơn 0.")
        continue_allowed = False
    elif budget < 100000:
        errors.append("💰 Ngân sách tối thiểu 100.000 ₫.")
        continue_allowed = False

    # 3. Kiểm tra số hành khách
    if not isinstance(pax, int) or pax < 1 or pax > 50:
        errors.append("👥 Số lượng hành khách phải từ 1 đến 50.")
        continue_allowed = False

    # 4. Kiểm tra ngày tháng (cho phép ngày về trùng ngày đi, nhưng giờ về phải sau giờ đi, tối đa 7 ngày)
    days = 1
    if date_start and date_end:
        try:
            ds = datetime.strptime(date_start, "%Y-%m-%d")
            de = datetime.strptime(date_end, "%Y-%m-%d")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # Kiểm tra ngày ở quá khứ
            if ds < today:
                errors.append("📅 Ngày khởi hành không được ở quá khứ.")
                continue_allowed = False
            diff = (de - ds).days
            days = max(diff, 1)
            # CONSTRAINT: tối đa 7 ngày
            if diff > 7:
                errors.append(
                    f"📅 Khoảng thời gian vượt quá 7 ngày (hiện tại: {diff} ngày)."
                )
                continue_allowed = False
            if diff < 0:
                errors.append("📅 Ngày kết thúc phải sau hoặc bằng ngày bắt đầu.")
                continue_allowed = False
            # Nếu cùng ngày, kiểm tra giờ
            if diff == 0:
                try:
                    dt_dep = datetime.strptime(departure_time, "%H:%M")
                    dt_ret = datetime.strptime(return_time, "%H:%M")
                    if dt_ret <= dt_dep:
                        errors.append(
                            "⏰ Trong cùng một ngày, giờ kết thúc phải sau giờ khởi hành."
                        )
                        continue_allowed = False
                except:
                    pass
        except ValueError:
            errors.append("📅 Định dạng ngày không hợp lệ.")
            continue_allowed = False
    else:
        errors.append("📅 Vui lòng chọn ngày khởi hành và ngày kết thúc.")
        continue_allowed = False

    # 5. BỔ SUNG: Kiểm tra điểm xuất phát (cảnh báo mềm)
    if not dep_city_id:
        errors.append(
            "📍 Bạn chưa nhập điểm xuất phát. Hệ thống sẽ mặc định xuất phát từ thành phố đích (chuyến đi nội tỉnh)."
        )
        # continue_allowed vẫn giữ nguyên (true)

    # 6. Kiểm tra phương tiện và lưu trú (các lỗi cứng/mềm)
    transport_issues = validate_transport(
        dep_city_id, city_id, transport, days, pax, budget
    )
    for typ, msg in transport_issues:
        errors.append(msg)
        if typ == "error":
            continue_allowed = False

    accom_issues = validate_accommodation(accommodation, budget, pax, days)
    for typ, msg in accom_issues:
        errors.append(msg)
        if typ == "error":
            continue_allowed = False

    # 7. DEMO: Kiểm tra giá thực tế (chỉ khi chưa có lỗi cứng nghiêm trọng)
    #    Lỗi này sẽ được phát hiện ở giai đoạn "kết quả", nhưng ta mô phỏng ở đây.
    if continue_allowed and city_id and budget > 0:
        demo_error, demo_msgs = simulate_actual_pricing_check(
            city_id, budget, pax, days
        )
        if demo_error:
            errors.extend(demo_msgs)
            # Đây là lỗi mềm (có thể tiếp tục nếu người dùng muốn) hoặc cứng tùy ý
            # Ở đây ta đặt là lỗi mềm để demo nút "Tiếp tục"
            continue_allowed = True  # vẫn cho phép tiếp tục dù thiếu ngân sách thực tế

    # ----- TRẢ VỀ KẾT QUẢ -----
    if errors:
        return jsonify(
            {"status": "error", "errors": errors, "continue_allowed": continue_allowed}
        )
    else:
        # Trong thực tế, ở đây sẽ gọi các API để tạo itinerary
        # Hiện tại chỉ trả về success để frontend chuyển sang màn hình result demo
        return jsonify({"status": "success"})


# ========== CÁC API KHÁC (giữ nguyên) ==========
@app.route("/api/book", methods=["POST"])
def api_book():
    available = random.random() > 0.05
    return jsonify({"available": available})


@app.route("/api/save", methods=["POST"])
def api_save():
    return jsonify({"status": "require_login"})


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    data = request.get_json() or {}
    feedback = data.get("feedback", "").strip()
    if not feedback:
        return jsonify({"status": "error", "message": "Phản hồi trống."})
    if len(feedback) > 500:
        return jsonify({"status": "error", "message": "Phản hồi tối đa 500 ký tự."})
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
