from flask import Flask, Response, render_template_string, url_for
import cv2
import time

app = Flask(__name__)

# 學號與基本資訊
STUDENT_ID = "M11382028"
STUDENT_NAME = "李景詮"
LOCATION = "大同路二段與健康路一段口(北)"

# 遠端 CCTV 串流 URL
VIDEO_URL = "https://trafficvideo2.tainan.gov.tw/54b2e135"

@app.route("/snapshot")
def snapshot():
    cap = cv2.VideoCapture(VIDEO_URL)
    success, frame = cap.read()
    cap.release()

    if not success:
        return Response("Failed to fetch image", status=503)

    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return Response("Encoding failed", status=500)

    return Response(buffer.tobytes(), mimetype='image/jpeg')

@app.route("/")
def index():
    return render_template_string("""
    <!doctype html>
    <html>
    <head>
        <title>台南即時監視器</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>台南即時影像串流 </h1>
        <p><strong>學號：</strong>{{ student_id }}</p>
        <p><strong>姓名：</strong>{{ student_name }}</p>
        <p><strong>監視器位置：</strong>{{ location }}</p>
        <img id="video" width="640" height="480" src="{{ url_for('snapshot') }}">
        <script>
            function reloadImage() {
                const img = document.getElementById("video");
                img.src = "{{ url_for('snapshot') }}" + "?" + new Date().getTime();  // 防止快取
            }
            setInterval(reloadImage, 1000);  // 每秒更新
        </script>
    </body>
    </html>
    """, student_id=STUDENT_ID, student_name=STUDENT_NAME, location=LOCATION)

@app.route("/test")
def home():
    return "This is test"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
