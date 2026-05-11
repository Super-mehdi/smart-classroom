import cv2
import time
import os
from dotenv import load_dotenv
from recognizer import load_embeddings, recognize_frame
from attendance import post_attendance
from logger import log_frame

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", 10))
SESSION_ID       = int(os.getenv("SESSION_ID", 0))

def main():
    if not SESSION_ID:
        print("ERROR: SESSION_ID is not set in .env. Exiting.")
        return

    load_embeddings()

    print(f"Starting camera loop for session {SESSION_ID}")
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

            frame_id += 1
            time.sleep(CAPTURE_INTERVAL)

    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        cap.release()
        print("Camera released.")

if __name__ == "__main__":
    main()
