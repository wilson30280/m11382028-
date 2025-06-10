from flask import Flask, Response, render_template_string
import cv2

app = Flask(__name__)

# 學號與基本資訊
STUDENT_ID = "M11382028"
STUDENT_NAME = "李景詮"
LOCATION = "大同路二段與健康路一段口(北"

# 遠端 CCTV 串流 URL
VIDEO_URL = "https://trafficvideo2.tainan.gov.tw/54b2e135"

def generate_frames():
    cap = cv2.VideoCapture(VIDEO_URL)
    
    if not cap.isOpened():
        yield b''
        return
    
    while True:
        success, frame = cap.read()
        if not success:
            # 嘗試重新連線
            cap.release()
            cap = cv2.VideoCapture(VIDEO_URL)
            continue

        # 轉成 JPEG 格式
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route("/test")
def home():
    return "This is test"

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/")
def index():
    # 顯示即時影像串流與個人資訊
    return render_template_string("""
    <html>
    <head><title>台南即時監視器</title></head>
    <body>
    <h1>台南即時影像串流</h1>
    <p><strong>學號：</strong>{{ student_id }}</p>
    <p><strong>姓名：</strong>{{ student_name }}</p>
    <p><strong>監視器位置：</strong>{{ location }}</p>
    <img src="{{ url_for('video_feed') }}" width="640" height="480">
    </body>
    </html>
    """, student_id=STUDENT_ID, student_name=STUDENT_NAME, location=LOCATION)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)