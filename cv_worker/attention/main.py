import cv2
import sys
import time

from cv_worker.attention.facemesh import FaceMeshDetector
from cv_worker.attention.head_pose import estimate_head_pose
from cv_worker.attention.ear import get_ear
from cv_worker.attention.attention_score import compute_attention_score
from cv_worker.attention.seat_grid import SeatGrid
from cv_worker.attention.aggregator import ScoreAggregator
import cv_worker.state as state

# ── config ───────────────────────────────────────────────
FRAME_W, FRAME_H = 640, 480
ROWS, COLS       = 3, 4

# ── setup grid ───────────────────────────────────────────
grid = SeatGrid(rows=ROWS, cols=COLS, frame_w=FRAME_W, frame_h=FRAME_H)
student_ids = [f"S{str(i).zfill(3)}" for i in range(1, 13)]
for i, sid in enumerate(student_ids):
    grid.assign_student(i // COLS, i % COLS, sid)

# ── setup components ─────────────────────────────────────
aggregator = ScoreAggregator(max_buffer=30)
detector   = FaceMeshDetector()


def open_camera():
    """Try DroidCam, then webcam fallbacks. Block and retry until one opens."""
    sources = [
        ("http://10.72.178.56:4747/video", "DroidCam"),
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
        print("No camera available. Retrying in 10 seconds...")
        time.sleep(10)


cap = open_camera()

# ── set active session in Redis ──────────────────────────
state.set_session(1)
print("Session started. Press Ctrl+C to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera read failed. Attempting to reopen...")
        cap.release()
        time.sleep(3)
        cap = open_camera()
        continue

    frame   = cv2.resize(frame, (FRAME_W, FRAME_H))
    results = detector.process(frame)
    frame_scores = {}

    if results:
        all_landmarks = detector.get_landmarks_array(results, frame.shape)

        for landmarks in all_landmarks:

            # determine seat from nose tip
            nose_x, nose_y, _ = landmarks[1]
            student_id = grid.get_student_id(nose_x, nose_y)
            if student_id is None:
                continue

            # head pose
            pose = estimate_head_pose(landmarks, FRAME_W, FRAME_H)
            if pose is None:
                continue
            yaw, pitch = pose

            # eye aspect ratio
            _, _, avg_ear = get_ear(landmarks)
            if avg_ear is None:
                continue

            # attention score
            score = compute_attention_score(yaw, pitch, avg_ear)
            frame_scores[student_id] = score

            # write to Redis shared state
            state.update(
                student_id=student_id,
                score=score,
                yaw=yaw,
                pitch=pitch,
                ear=avg_ear,
            )

    # feed into aggregator
    aggregator.add_frame_scores(frame_scores)

    # print rolling averages
    averages  = aggregator.get_all_averages()
    class_avg = aggregator.get_class_average()

    if averages:
        print("Rolling averages:")
        for sid, avg in averages.items():
            print(f"  {sid}: {avg:.4f}")
        print(f"  Class avg: {class_avg:.4f}\n")

# ── cleanup ──────────────────────────────────────────────
cap.release()
detector.close()
aggregator.reset()
state.clear_session()
print("Session ended.")