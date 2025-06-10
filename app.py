from flask import Flask, Response, render_template_string
import cv2
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 學號與基本資訊
STUDENT_ID = "M11382028"
STUDENT_NAME = "李景詮"
LOCATION = "大同路二段與健康路一段口(北"

# CCTV 串流 URL
VIDEO_URL = "https://trafficvideo2.tainan.gov.tw/54b2e135"

# 股票代碼與名稱對應
STOCKS = {
    "2330.TW": "台積電",
    "2317.TW": "鴻海",
    "2382.TW": "廣達"
}

def generate_frames():
    cap = cv2.VideoCapture(VIDEO_URL)

    if not cap.isOpened():
        yield b''
        return

    while True:
        success, frame = cap.read()
        if not success:
            cap.release()
            cap = cv2.VideoCapture(VIDEO_URL)
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def fetch_stock_info(stock_code):
    url = f'https://tw.stock.yahoo.com/quote/{stock_code}'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    try:
        title = soup.find('h1').get_text(strip=True)
        price = soup.select_one('.Fz\\(32px\\)').get_text(strip=True)
        change = soup.select_one('.Fz\\(20px\\)').get_text(strip=True)
        
        if soup.select_one('.C\\(\\$c-trend-down\\)'):
            sign = '-'
        elif soup.select_one('.C\\(\\$c-trend-up\\)'):
            sign = '+'
        else:
            sign = ''
        return f"{title} : {price} ({sign}{change})"
    except Exception:
        return f"{stock_code} 資料錯誤"

@app.route("/")
def index():
    return render_template_string("""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>台南即時監視器</title>
    </head>
    <body>
        <h1>台南即時影像串流</h1>
        <p><strong>學號：</strong>{{ student_id }}</p>
        <p><strong>姓名：</strong>{{ student_name }}</p>
        <p><strong>監視器位置：</strong>{{ location }}</p>
        <img src="{{ url_for('video_feed') }}" width="640" height="480">
        <hr>
        <p><a href="/stocks">查看台股資訊</a></p>
    </body>
    </html>
    """, student_id=STUDENT_ID, student_name=STUDENT_NAME, location=LOCATION)

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stocks")
def stock_page():
    stock_data = [fetch_stock_info(code) for code in STOCKS]
    return render_template_string("""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>即時股價</title>
    </head>
    <body>
        <h1>即時股價資訊</h1>
        <ul>
        {% for stock in stock_data %}
            <li>{{ stock }}</li>
        {% endfor %}
        </ul>
        <a href="/">返回即時監視器</a>
    </body>
    </html>
    """, stock_data=stock_data)

@app.route("/test")
def home():
    return "This is test"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

