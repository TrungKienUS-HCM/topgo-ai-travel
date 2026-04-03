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
        "img": "/static/img/cities/ha-noi.jpg",
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
    ],
    "hoian": [
        "Phố Cổ Hội An",
        "Chùa Cầu",
        "Làng rau Trà Quế",
        "Biển Cửa Đại",
        "Làng gốm Thanh Hà",
        "Mỳ Cao Lầu",
    ],
    "ha": [
        "Hồ Hoàn Kiếm",
        "Lăng Chủ tịch Hồ Chí Minh",
        "Văn Miếu – Quốc Tử Giám",
        "Phố cổ 36 phố phường",
        "Hồ Tây",
        "Chùa Một Cột",
        "Hoàng Thành Thăng Long",
    ],
    "hcm": [
        "Nhà thờ Đức Bà",
        "Địa đạo Củ Chi",
        "Chợ Bến Thành",
        "Bảo tàng Chứng tích Chiến tranh",
        "Dinh Độc Lập",
        "Phố đi bộ Nguyễn Huệ",
    ],
    "nt": [
        "Tháp Bà Ponagar",
        "Vinpearl Land",
        "Vịnh Nha Trang",
        "Đảo Hòn Mun",
        "Chùa Long Sơn",
        "Biển Bãi Dài",
    ],
    "dl": [
        "Hồ Xuân Hương",
        "Thung lũng Tình Yêu",
        "Đỉnh LangBiang",
        "Làng hoa Vạn Thành",
        "Làng Cù Lần",
        "Dinh Bảo Đại",
    ],
    "ph": [
        "Grand World Phú Quốc",
        "Bãi Sao",
        "Cáp treo Hòn Thơm",
        "Vinpearl Safari",
        "Chợ đêm Phú Quốc",
        "Bãi Dài",
    ],
    "hue": [
        "Đại Nội – Hoàng Thành Huế",
        "Lăng Tự Đức",
        "Chùa Thiên Mụ",
        "Lăng Khải Định",
        "Cầu Trường Tiền",
        "Chợ Đông Ba",
    ],
    "qni": [
        "Ghềnh Ráng Tiên Sa",
        "Eo Gió",
        "Kỳ Co",
        "Thành Hoàng Đế",
        "Bãi biển Quy Nhơn",
        "Bãi Xép",
    ],
    "hl": [
        "Vịnh Hạ Long",
        "Hang Sửng Sốt",
        "Đảo Ti Tốp",
        "Làng chài Cửa Vạn",
        "Đảo Cát Bà",
        "Núi Bài Thơ",
    ],
}

# Approximate road distances between cities (km)
# === TẠM THỜI GÁN CỨNG - SAU SẼ TÍCH HỢP DỮ LIỆU THỰC TẾ ===
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

# Minimum budget per person for each transport type (VND, one-way)
# === TẠM THỜI GÁN CỨNG - SAU SẼ TÍCH HỢP DỮ LIỆU THỰC TẾ ===
TRANSPORT_MIN_PER_PAX = {
    "Máy bay": 700_000,
    "Tàu hỏa": 200_000,
    "Xe khách": 150_000,
    "Ô tô riêng": 0,  # fuel cost, variable
    "Thuê ô tô tự lái": 400_000,
    "Xe máy": 0,
}

# Suggested minimum budget per night per room for accommodation types
# === TẠM THỜI GÁN CỨNG - SAU SẼ TÍCH HỢP DỮ LIỆU THỰC TẾ ===
ACCOMMODATION_MIN_PER_NIGHT = {
    "Resort": 1_200_000,
    "Villa": 1_500_000,
    "Khách sạn": 400_000,
    "Homestay": 250_000,
    "Airbnb": 350_000,
    "Căn hộ": 300_000,
}


def validate_transport(city_id, dep_city_id, transport, days, pax, budget):
    """Return list of error strings related to transport/budget feasibility."""
    errors = []

    distance = CITY_DISTANCES.get((dep_city_id, city_id)) if dep_city_id else None

    if transport == "Xe đạp":
        errors.append(
            "Xe đạp không phù hợp cho các chuyến du lịch liên tỉnh. Vui lòng chọn phương tiện khác."
        )
        return errors

    if distance is not None and distance > 0:
        if transport == "Xe máy":
            if distance > 800:
                errors.append(
                    f"Xe máy không phù hợp cho quãng đường {distance} km. Hãy chọn xe khách, tàu hỏa hoặc máy bay."
                )
            elif distance > 500:
                errors.append(
                    f"⚠️ Quãng đường {distance} km bằng xe máy rất vất vả và nguy hiểm. Cân nhắc phương tiện khác."
                )

        if transport == "Xe khách" and distance > 800:
            errors.append(
                f"⚠️ Xe khách cho {distance} km sẽ mất 15–20 tiếng. Hãy cân nhắc tàu hỏa hoặc máy bay."
            )

        if transport in ("Ô tô riêng", "Thuê ô tô tự lái"):
            if distance >= 1500:
                errors.append(
                    f"❌ Quãng đường {distance} km bằng ô tô cần ít nhất 3–4 ngày (hiện tại: {days} ngày). Đề xuất chọn máy bay."
                )
            elif distance > 700 and days <= 1:
                errors.append(
                    f"⚠️ Lái xe {distance} km mất 8–12 tiếng, không khả thi trong {days} ngày. Cân nhắc máy bay hoặc tàu."
                )

        if transport == "Máy bay":
            min_flight = pax * TRANSPORT_MIN_PER_PAX["Máy bay"] * 2  # round-trip
            if budget < min_flight:
                errors.append(
                    f"💰 Ngân sách quá thấp cho vé máy bay khứ hồi. Cần tối thiểu ~{min_flight:,} ₫ cho {pax} người. (Hiện tại: {budget:,} ₫)"
                )

        # Check rental car extra cost
        if transport == "Thuê ô tô tự lái":
            rental_cost = 500_000 * days  # 500k per day
            if budget < rental_cost:
                errors.append(
                    f"💰 Ngân sách không đủ cho thuê xe tự lái {days} ngày (tối thiểu {rental_cost:,} ₫). Hãy chọn phương tiện khác hoặc tăng ngân sách."
                )

    return errors


def validate_accommodation(accommodation, budget, pax, days):
    """Check if budget is enough for the chosen accommodation type."""
    if not accommodation or not budget or not pax or not days:
        return []
    errors = []
    min_per_night = ACCOMMODATION_MIN_PER_NIGHT.get(accommodation, 200_000)
    # Assuming 1 room for 2 pax, otherwise need more rooms
    rooms_needed = (pax + 1) // 2
    total_min_accommodation = min_per_night * rooms_needed * days
    if budget < total_min_accommodation:
        errors.append(
            f"💰 Ngân sách không đủ cho loại hình {accommodation} với {pax} người trong {days} ngày. Cần tối thiểu ~{total_min_accommodation:,} ₫ cho chỗ ở (giả sử {rooms_needed} phòng)."
        )
    return errors


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

    errors = []
    continue_allowed = True  # sẽ set False nếu có lỗi cứng

    # ----- Lỗi cứng (không thể tiếp tục) -----
    if not city_id:
        errors.append("📍 Chưa chọn thành phố muốn đến.")
        continue_allowed = False

    if budget < 10000:
        errors.append("💰 Ngân sách tối thiểu 10.000 ₫.")
        continue_allowed = False

    days = 1
    if date_start and date_end:
        try:
            ds = datetime.strptime(date_start, "%Y-%m-%d")
            de = datetime.strptime(date_end, "%Y-%m-%d")
            diff = (de - ds).days
            days = max(diff, 1)
            if diff > 30:
                errors.append(
                    f"📅 Khoảng thời gian vượt quá 30 ngày (hiện tại: {diff} ngày)."
                )
                continue_allowed = False
            if de <= ds:
                errors.append("📅 Ngày kết thúc phải sau ngày bắt đầu.")
                continue_allowed = False
        except ValueError:
            errors.append("📅 Định dạng ngày không hợp lệ.")
            continue_allowed = False

    # Khoảng cách
    distance = None
    if dep_city_id and city_id:
        distance = CITY_DISTANCES.get((dep_city_id, city_id))

    # Lỗi cứng về phương tiện
    if transport == "Xe đạp":
        errors.append(
            "Xe đạp không phù hợp cho các chuyến du lịch liên tỉnh. Vui lòng chọn phương tiện khác."
        )
        continue_allowed = False

    if distance is not None and distance > 0:
        if transport == "Xe máy" and distance > 800:
            errors.append(
                f"Xe máy không phù hợp cho quãng đường {distance} km. Hãy chọn xe khách, tàu hỏa hoặc máy bay."
            )
            continue_allowed = False
        if (
            transport in ("Ô tô riêng", "Thuê ô tô tự lái")
            and distance >= 1500
            and days < 3
        ):
            errors.append(
                f"❌ Quãng đường {distance} km bằng ô tô cần ít nhất 3–4 ngày (hiện tại: {days} ngày). Đề xuất chọn máy bay."
            )
            continue_allowed = False

        # Kiểm tra ngân sách vé máy bay (lỗi cứng)
        if transport == "Máy bay":
            min_flight = pax * TRANSPORT_MIN_PER_PAX["Máy bay"] * 2
            if budget < min_flight:
                errors.append(
                    f"💰 Ngân sách quá thấp cho vé máy bay khứ hồi. Cần tối thiểu ~{min_flight:,} ₫ cho {pax} người. (Hiện tại: {budget:,} ₫)"
                )
                continue_allowed = False

        # Kiểm tra ngân sách thuê xe tự lái (lỗi cứng)
        if transport == "Thuê ô tô tự lái":
            rental_cost = 500_000 * days
            if budget < rental_cost:
                errors.append(
                    f"💰 Ngân sách không đủ cho thuê xe tự lái {days} ngày (tối thiểu {rental_cost:,} ₫). Hãy chọn phương tiện khác hoặc tăng ngân sách."
                )
                continue_allowed = False

    # Kiểm tra ngân sách chỗ ở (lỗi cứng)
    if accommodation:
        min_per_night = ACCOMMODATION_MIN_PER_NIGHT.get(accommodation, 200_000)
        rooms_needed = (pax + 1) // 2
        total_min_accommodation = min_per_night * rooms_needed * days
        if budget < total_min_accommodation:
            errors.append(
                f"💰 Ngân sách không đủ cho loại hình {accommodation} với {pax} người trong {days} ngày. Cần tối thiểu ~{total_min_accommodation:,} ₫ cho chỗ ở (giả sử {rooms_needed} phòng)."
            )
            continue_allowed = False

    # ----- Cảnh báo mềm (vẫn cho phép tiếp tục) -----
    # Chỉ thêm cảnh báo nếu chưa có lỗi cứng (để tránh spam)
    if continue_allowed:
        # Ngân sách tối thiểu 200k/người/ngày (cảnh báo, không chặn)
        min_budget = pax * days * 200_000
        if budget < min_budget:
            errors.append(
                f"⚠️ Ngân sách thấp hơn mức khuyến nghị (tối thiểu ~{min_budget:,} ₫ cho {pax} người × {days} ngày). Bạn vẫn có thể tiếp tục nhưng trải nghiệm có thể bị ảnh hưởng."
            )

        # Cảnh báo phương tiện mềm
        if distance is not None and distance > 0:
            if transport == "Xe máy" and 500 < distance <= 800:
                errors.append(
                    f"⚠️ Quãng đường {distance} km bằng xe máy rất vất vả và nguy hiểm. Cân nhắc phương tiện khác."
                )
            if transport == "Xe khách" and distance > 800:
                errors.append(
                    f"⚠️ Xe khách cho {distance} km sẽ mất 15–20 tiếng. Hãy cân nhắc tàu hỏa hoặc máy bay."
                )
            if (
                transport in ("Ô tô riêng", "Thuê ô tô tự lái")
                and distance > 700
                and days <= 1
            ):
                errors.append(
                    f"⚠️ Lái xe {distance} km mất 8–12 tiếng, không khả thi trong {days} ngày. Cân nhắc máy bay hoặc tàu."
                )

    if errors:
        return jsonify(
            {"status": "error", "errors": errors, "continue_allowed": continue_allowed}
        )

    return jsonify({"status": "success"})


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
