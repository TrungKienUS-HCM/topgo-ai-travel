import random
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory

app = Flask(__name__)

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
    budget = data.get("budget", 0)
    pax = data.get("pax", 1)
    date_start = data.get("date_start", "")
    date_end = data.get("date_end", "")
    transport = data.get("transport", "")
    accommodation = data.get("accommodation", "")
    departure_time = data.get("departure_time", "07:00")
    return_time = data.get("return_time", "18:00")

    errors = []

    if not city_id:
        errors.append("Chưa chọn thành phố")

    if budget < 10000:
        errors.append("Ngân sách tối thiểu 10.000 ₫")

    if date_start and date_end:
        try:
            ds = datetime.strptime(date_start, "%Y-%m-%d")
            de = datetime.strptime(date_end, "%Y-%m-%d")
            diff = (de - ds).days
            if diff > 30:
                errors.append(
                    f"Khoảng thời gian vượt quá 30 ngày (hiện tại: {diff} ngày)"
                )
            if de <= ds:
                errors.append("Ngày kết thúc phải sau ngày bắt đầu")
        except ValueError:
            errors.append("Định dạng ngày không hợp lệ")

    if not errors and pax and budget and date_start and date_end:
        try:
            ds = datetime.strptime(date_start, "%Y-%m-%d")
            de = datetime.strptime(date_end, "%Y-%m-%d")
            days = max((de - ds).days, 1)
            min_budget = pax * days * 200000
            if budget < min_budget:
                errors.append(
                    f"Ngân sách quá thấp (~{min_budget:,} ₫ tối thiểu cho {pax} người × {days} ngày)"
                )
        except Exception:
            pass

    if errors:
        return jsonify({"status": "error", "errors": errors})

    # Mock success
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
        return jsonify({"status": "error", "message": "Feedback trống"})
    if len(feedback) > 500:
        return jsonify({"status": "error", "message": "Feedback tối đa 500 ký tự"})
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
