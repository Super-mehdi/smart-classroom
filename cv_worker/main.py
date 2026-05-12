# cv_worker/main.py

import cv2
import time
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# ── absence pipeline imports ──────────────────
from cv_absence.recognizer import load_embeddings, recognize_frame
from cv_absence.attendance import post_attendance
from cv_absence.logger import log_frame

# ── attention pipeline imports ────────────────
from attention.facemesh import FaceMeshDetector
from attention.head_pose import estimate_head_pose
from attention.ear import get_ear
from attention.attention_score import compute_attention_score
from attention.aggregator import ScoreAggregator
import state

# ── config ────────────────────────────────────
SESSION_ID       = int(os.getenv("SESSION_ID", 1))
CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", 10))
CAMERA_URL       = os.getenv("CAMERA_URL", "0")
FRAME_W, FRAME_H = 640, 480

# convert "0" string to int for local webcam
camera_source = int(CAMERA_URL) if CAMERA_URL.isdigit() else CAMERA_URL

# ── setup ─────────────────────────────────────
print(f"Starting unified CV worker — session {SESSION_ID}")
print(f"Camera: {CAMERA_URL}")
print(f"Absence check every: {CAPTURE_INTERVAL}s")

# absence setup — load face embeddings from MongoDB
load_embeddings()

# attention setup
detector   = FaceMeshDetector()
aggregator = ScoreAggregator(max_buffer=30)

# set active session in Redis for Celery attention task
state.set_session(SESSION_ID)

# camera
cap = cv2.VideoCapture(camera_source)
if not cap.isOpened():
    print(f"ERROR: Could not open camera: {CAMERA_URL}")
    sys.exit(1)

frame_id          = 0
last_absence_time = 0
last_bboxes       = []
last_present      = []

print("Running. Press Ctrl+C to stop.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("WARNING: Failed to grab frame, retrying...")
            time.sleep(1)
            continue

        frame        = cv2.resize(frame, (FRAME_W, FRAME_H))
        current_time = time.time()

        # ── ABSENCE PIPELINE ─────────────────────────
        # runs every CAPTURE_INTERVAL seconds (default 10s)
        if current_time - last_absence_time >= CAPTURE_INTERVAL:
            last_absence_time = current_time

            result       = recognize_frame(frame)
            last_present = result["present"]
            absent       = result["absent"]
            last_bboxes  = result.get("bboxes", [])

            print(f"[{time.strftime('%H:%M:%S')}] Absence check")
            print(f"  Present: {[s['name'] for s in last_present]}")
            print(f"  Absent:  {[s['name'] for s in absent]}")

            post_attendance(SESSION_ID, last_present, absent)
            log_frame(
                SESSION_ID,
                frame_id,
                len(last_present),
                len(last_present) + len(absent)
            )

        # ── ATTENTION PIPELINE ────────────────────────
        # runs every frame
        results      = detector.process(frame)
        frame_scores = {}

        if results:
            all_landmarks = detector.get_landmarks_array(results, frame.shape)

            for landmarks in all_landmarks:
                nose_x, nose_y, _ = landmarks[1]

                # match this face to a recognized student_id
                # by checking if nose tip falls inside a DeepFace bbox
                student_id = None
                for bbox in last_bboxes:
                    x, y, w, h = bbox["x"], bbox["y"], bbox["w"], bbox["h"]
                    if x <= nose_x <= x + w and y <= nose_y <= y + h:
                        for s in last_present:
                            if s["name"] == bbox["name"]:
                                student_id = s["student_id"]
                                break
                        break

                # skip unknown faces — no student_id = not enrolled
                if student_id is None:
                    continue

                # head pose
                pose = estimate_head_pose(landmarks, FRAME_W, FRAME_H)
                if pose is None:
                    continue
                yaw, pitch = pose

                # EAR
                _, _, avg_ear = get_ear(landmarks)
                if avg_ear is None:
                    continue

                # attention score
                score = compute_attention_score(yaw, pitch, avg_ear)
                frame_scores[student_id] = score

                # write to Redis for Celery task
                state.update(
                    student_id=student_id,
                    score=score,
                    yaw=yaw,
                    pitch=pitch,
                    ear=avg_ear,
                )

        # feed aggregator
        aggregator.add_frame_scores(frame_scores)

        # log every 30 frames
        if frame_id % 30 == 0 and frame_scores:
            class_avg = aggregator.get_class_average()
            print(f"[{time.strftime('%H:%M:%S')}] Attention — "
                  f"tracking {len(frame_scores)} student(s) — "
                  f"class avg: {class_avg:.2f}" if class_avg else
                  f"[{time.strftime('%H:%M:%S')}] Attention — "
                  f"tracking {len(frame_scores)} student(s)")

        frame_id += 1
        time.sleep(0.01)   # yield to avoid 100% CPU

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    cap.release()
    detector.close()
    aggregator.reset()
    state.clear_session()
    print("Session ended cleanly.")