from flask import Flask, Response, render_template_string, url_for
import cv2
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 學號與基本資訊
STUDENT_ID = "M11382028"
STUDENT_NAME = "李景詮"
LOCATION = "大同路二段與健康路一段口(北)"

# 遠端 CCTV 串流 URL
VIDEO_URL = "https://trafficvideo2.tainan.gov.tw/54b2e135"

# 股票代碼
STOCK_SYMBOL = "2330.TW"
STOCK_URL = f"https://tw.stock.yahoo.com/quote/{STOCK_SYMBOL}"

@app.route("/snapshot")
def snapshot():
    try:
        cap = cv2.VideoCapture(VIDEO_URL)
        if not cap.isOpened():
            return Response("無法開啟影像來源", status=503)

        success, frame = cap.read()
        cap.release()

        if not success:
            return Response("無法讀取影像", status=503)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            return Response("影像編碼失敗", status=500)

        return Response(buffer.tobytes(), mimetype='image/jpeg')

    except Exception as e:
        return Response(f"伺服器錯誤：{str(e)}", status=500)

@app.route("/stock")
def stock():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(STOCK_URL, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.find("h1").get_text()
        price = soup.select_one(".Fz\\(32px\\)").get_text()
        diff = soup.select_one(".Fz\\(20px\\)").get_text()

        # 判斷漲跌
        if soup.select("#main-0-QuoteHeader-Proxy .C\\(\\$c-trend-up\\)"):
            sign = "+"
        elif soup.select("#main-0-QuoteHeader-Proxy .C\\(\\$c-trend-down\\)"):
            sign = "-"
        else:
            sign = ""

        return f"{title} : {price} ({sign}{diff})"

    except Exception as e:
        return f"取得股票資訊失敗：{str(e)}"

@app.route("/")
def index():
    return render_template_string("""
    <!doctype html>
    <html lang="zh-TW">
    <head>
        <meta charset="utf-8">
        <title>台南即時監視器 + 台積電股價</title>
        <style>
            body { font-family: sans-serif; padding: 20px; }
            img { border: 2px solid #ccc; }
        </style>
    </head>
    <body>
        <h1>台南即時影像與股價資訊</h1>
        <p><strong>學號：</strong>{{ student_id }}</p>
        <p><strong>姓名：</strong>{{ student_name }}</p>
        <p><strong>監視器位置：</strong>{{ location }}</p>

        <h2>🎥 即時影像（每秒更新）</h2>
        <img id="video" width="640" height="480" src="{{ url_for('snapshot') }}">

        <h2>📈 台積電股價（每 30 秒更新）</h2>
        <div id="stock">載入中...</div>

        <script>
            // 每秒更新影像
            function reloadImage() {
                const img = document.getElementById("video");
                img.src = "{{ url_for('snapshot') }}" + "?" + new Date().getTime();
            }
            setInterval(reloadImage, 1000);

            // 每 30 秒更新股價
            async function updateStock() {
                const res = await fetch("/stock");
                const text = await res.text();
                document.getElementById("stock").innerText = text;
            }
            updateStock();
            setInterval(updateStock, 30000);
        </script>
    </body>
    </html>
    """, student_id=STUDENT_ID, student_name=STUDENT_NAME, location=LOCATION)

@app.route("/test")
def home():
    return "This is test"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
