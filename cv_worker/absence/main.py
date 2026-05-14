import cv2
import time
import os
import threading
from dotenv import load_dotenv
from flask import Flask, Response

from recognizer import load_embeddings, recognize_frame
from attendance import post_attendance
from logger import log_frame

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", 10))
SESSION_ID       = int(os.getenv("SESSION_ID", 0))

app = Flask(__name__)
current_frame = None
lock = threading.Lock()

def generate_frames():
    global current_frame
    while True:
        with lock:
            if current_frame is None:
                continue
            ret, buffer = cv2.imencode('.jpg', current_frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.05)

@app.route('/')
def index():
    return "CV Worker is running. <a href='/video_feed'>View live camera feed</a>"

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def main_loop():
    global current_frame
    if not SESSION_ID:
        print("ERROR: SESSION_ID is not set in .env. Exiting.")
        return

    load_embeddings()

    print(f"Starting camera loop for session {SESSION_ID}")
    print(f"Sampling every {CAPTURE_INTERVAL} seconds")

    cap = cv2.VideoCapture("http://10.168.37.95:4747/video")
    if not cap.isOpened():
        print("ERROR: Could not open camera. Exiting.")
        return

    frame_id = 0
    last_capture_time = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("WARNING: Failed to grab frame, retrying...")
                time.sleep(2)
                continue

            current_time = time.time()
            # Perform heavy recognition every CAPTURE_INTERVAL seconds
            if current_time - last_capture_time >= CAPTURE_INTERVAL:
                last_capture_time = current_time
                
                # recognize_frame will modify frame in place to draw bounding boxes
                result       = recognize_frame(frame)
                present      = result["present"]
                absent       = result["absent"]
                face_count   = len(present)
                total        = len(present) + len(absent)

                print(f"[{time.strftime('%H:%M:%S')}] Frame {frame_id}")
                print(f"  Present ({face_count}): {[s['name'] for s in present]}")
                print(f"  Absent  ({len(absent)}): {[s['name'] for s in absent]}")

                post_attendance(SESSION_ID, present, absent)
                log_frame(SESSION_ID, frame_id, face_count, total)
                
                # Retrieve bboxes from the result
                last_bboxes = result.get("bboxes", [])
                frame_id += 1
            
            # Draw persistent bounding boxes on the current frame
            for bbox in last_bboxes:
                x, y, w, h = bbox["x"], bbox["y"], bbox["w"], bbox["h"]
                name_to_draw = bbox["name"]
                if w > 0 and h > 0:
                    color = (0, 255, 0) if name_to_draw != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, name_to_draw, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
            with lock:
                current_frame = frame.copy()
            
            # yield to let other threads run
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        cap.release()
        print("Camera released.")

def main():
    t = threading.Thread(target=main_loop)
    t.daemon = True
    t.start()
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()
