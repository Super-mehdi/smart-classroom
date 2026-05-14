import cv2
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── absence pipeline ──────────────────────────────────
from absence.recognizer import load_embeddings, recognize_frame
from absence.attendance import post_attendance
from absence.logger import log_frame

# ── attention pipeline ────────────────────────────────
from attention.facemesh import FaceMeshDetector
from attention.head_pose import estimate_head_pose
from attention.ear import get_ear
from attention.attention_score import compute_attention_score
from attention.aggregator import ScoreAggregator
from attention.face_id import FaceIdentifier, compute_simple_embedding
import state

# ── config ────────────────────────────────────────────
SESSION_ID       = int(os.getenv("SESSION_ID", 1))
ABSENCE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", 10))
FRAME_W, FRAME_H = 640, 480

# ── setup ─────────────────────────────────────────────
print(f"Starting unified CV worker — session {SESSION_ID}")

load_embeddings()

detector   = FaceMeshDetector()
aggregator = ScoreAggregator(max_buffer=30)
identifier = FaceIdentifier(similarity_threshold=0.80)

state.set_session(SESSION_ID)

# face identity cache — maps grid cell → student_id
# persists between absence checks so we don't lose identity
face_id_cache: dict[str, str] = {}


def get_cached_student_id(
    nose_x: int,
    nose_y: int,
    bboxes: list,
    present: list,
) -> str | None:
    """
    Match nose tip to a DeepFace bbox.
    Cache the result so it persists between absence checks.
    Falls back to cache if no current bbox match.
    """
    cell_key = f"{nose_x // 80}_{nose_y // 60}"

    for bbox in bboxes:
        x, y, w, h = bbox["x"], bbox["y"], bbox["w"], bbox["h"]
        if x <= nose_x <= x + w and y <= nose_y <= y + h:
            for s in present:
                if s["name"] == bbox["name"]:
                    face_id_cache[cell_key] = s["student_id"]
                    return s["student_id"]

    if cell_key in face_id_cache:
        return face_id_cache[cell_key]

    return None


def open_camera():
    sources = [
        ("http://10.168.37.95:4747/video", "DroidCam"),
        (0, "webcam index 0"),
        (2, "webcam index 2"),
    ]
    while True:
        for src, label in sources:
            cap = cv2.VideoCapture(src)
            if cap.isOpened():
                print(f"Camera opened: {label}")
                return cap
            cap.release()
        print("No camera available. Retrying in 10s...")
        time.sleep(10)


cap               = open_camera()
frame_id          = 0
last_absence_time = 0
last_bboxes       = []
last_present      = []

print(f"Absence check every {ABSENCE_INTERVAL}s. Press Ctrl+C to stop.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera read failed. Reopening...")
            cap.release()
            time.sleep(3)
            cap = open_camera()
            continue

        frame        = cv2.resize(frame, (FRAME_W, FRAME_H))
        current_time = time.time()

        # ── ABSENCE (every ABSENCE_INTERVAL seconds) ──────
        if current_time - last_absence_time >= ABSENCE_INTERVAL:
            last_absence_time = current_time

            result      = recognize_frame(frame)
            present     = result["present"]
            absent      = result["absent"]
            last_bboxes = result.get("bboxes", [])
            last_present = present

            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"Present: {[s['name'] for s in present]} | "
                  f"Absent:  {[s['name'] for s in absent]}")

            post_attendance(SESSION_ID, present, absent)
            log_frame(SESSION_ID, frame_id,
                      len(present), len(present) + len(absent))
            frame_id += 1

        # draw absence bboxes
        for bbox in last_bboxes:
            x, y, w, h = bbox["x"], bbox["y"], bbox["w"], bbox["h"]
            name  = bbox["name"]
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            if w > 0 and h > 0:
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, name, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # ── ATTENTION (every frame) ───────────────────────
        results      = detector.process(frame)
        frame_scores = {}

        if results:
            all_landmarks = detector.get_landmarks_array(results, frame.shape)

            for landmarks in all_landmarks:
                nose_x, nose_y, _ = landmarks[1]

                # try to get real student_id from absence pipeline
                student_id = get_cached_student_id(
                    nose_x, nose_y, last_bboxes, last_present
                )

                # fallback to face embedding identity
                if student_id is None:
                    embedding  = compute_simple_embedding(landmarks)
                    student_id = identifier.identify(embedding)

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

                # draw attention overlay
                color = (int(255 * (1 - score)), int(255 * score), 0)
                cv2.putText(frame, f"{student_id}",
                            (nose_x - 40, nose_y - 55),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(frame, f"Score: {score:.2f}",
                            (nose_x - 40, nose_y - 35),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                cv2.putText(frame, f"y:{yaw:.0f} p:{pitch:.0f}",
                            (nose_x - 40, nose_y - 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)

        # aggregator
        aggregator.add_frame_scores(frame_scores)
        averages  = aggregator.get_all_averages()
        class_avg = aggregator.get_class_average()

        if averages:
            print("Attention:")
            for sid, avg in averages.items():
                print(f"  {sid}: {avg:.4f}")
            if class_avg:
                print(f"  Class avg: {class_avg:.4f}\n")

        # overlays
        if class_avg is not None:
            cv2.putText(frame, f"Class avg: {class_avg:.2f}",
                        (10, FRAME_H - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (255, 255, 0), 2)

        cv2.putText(frame,
                    f"Session {SESSION_ID} | "
                    f"Faces: {identifier.get_enrolled_count()}",
                    (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

        cv2.imshow("SmartClass CV Worker", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    aggregator.reset()
    state.clear_session()
    print("Session ended.")