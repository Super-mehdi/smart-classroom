import cv2
import time
import os
from dotenv import load_dotenv
from detector import count_faces
from attendance import post_attendance
from logger import log_frame

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", 10))
SESSION_ID       = int(os.getenv("SESSION_ID", 0))
ENROLLED_COUNT   = int(os.getenv("ENROLLED_COUNT", 0))

def main():
    if not SESSION_ID:
        print("ERROR: SESSION_ID is not set in .env. Exiting.")
        return
    if not ENROLLED_COUNT:
        print("ERROR: ENROLLED_COUNT is not set in .env. Exiting.")
        return

    print(f"Starting camera loop for session {SESSION_ID}")
    print(f"Enrolled students: {ENROLLED_COUNT}")
    print(f"Sampling every {CAPTURE_INTERVAL} seconds")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open camera. Exiting.")
        return

    frame_id = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("WARNING: Failed to grab frame, retrying...")
                time.sleep(2)
                continue

            face_count = count_faces(frame)
            absent     = max(0, ENROLLED_COUNT - face_count)
            print(f"[{time.strftime('%H:%M:%S')}] Frame {frame_id} — {face_count} present, {absent} absent")

            post_attendance(SESSION_ID, face_count, ENROLLED_COUNT)
            log_frame(SESSION_ID, frame_id, face_count, ENROLLED_COUNT)

            frame_id += 1
            time.sleep(CAPTURE_INTERVAL)

    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        cap.release()
        print("Camera released.")

if __name__ == "__main__":
    main()