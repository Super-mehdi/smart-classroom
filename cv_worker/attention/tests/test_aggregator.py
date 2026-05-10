import cv2
import sys
sys.path.append("../..")

from attention.facemesh import FaceMeshDetector
from attention.head_pose import estimate_head_pose
from attention.ear import get_ear
from attention.attention_score import compute_attention_score
from attention.seat_grid import SeatGrid
from attention.aggregator import ScoreAggregator
import state

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

# try DroidCam, fall back to webcam
cap = cv2.VideoCapture("http://10.72.176.252:4747/video")
if not cap.isOpened():
    print("DroidCam not available, falling back to webcam index 0")
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("No camera available, falling back to webcam index 2")
    cap = cv2.VideoCapture(2)

# ── set active session in Redis ──────────────────────────
state.set_session(1)
print("Session started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

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

            # draw on frame
            cell = grid.get_cell(nose_x, nose_y)
            if cell:
                row, col = cell
                cell_w   = FRAME_W // COLS
                cell_h   = FRAME_H // ROWS
                cx       = col * cell_w + cell_w // 2
                cy       = row * cell_h + cell_h // 2
                color    = (int(255 * (1 - score)), int(255 * score), 0)

                cv2.putText(frame, f"{student_id}",
                            (cx - 30, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                cv2.putText(frame, f"{score:.2f}",
                            (cx - 20, cy + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                cv2.putText(frame, f"y:{yaw:.0f} p:{pitch:.0f}",
                            (cx - 30, cy + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

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

    # draw grid lines
    for r in range(1, ROWS):
        cv2.line(frame,
                 (0, r * FRAME_H // ROWS),
                 (FRAME_W, r * FRAME_H // ROWS),
                 (50, 50, 50), 1)
    for c in range(1, COLS):
        cv2.line(frame,
                 (c * FRAME_W // COLS, 0),
                 (c * FRAME_W // COLS, FRAME_H),
                 (50, 50, 50), 1)

    # class average overlay
    if class_avg is not None:
        cv2.putText(frame, f"Class avg: {class_avg:.2f}",
                    (10, FRAME_H - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 0), 2)

    cv2.imshow("Seat Grid Aggregator", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ── cleanup ──────────────────────────────────────────────
cap.release()
cv2.destroyAllWindows()
detector.close()
aggregator.reset()
state.clear_session()
print("Session ended.")