import cv2
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from facemesh import FaceMeshDetector
from head_pose import estimate_head_pose
from ear import get_ear
from attention_score import compute_attention_score
from aggregator import ScoreAggregator
from face_id import FaceIdentifier, compute_simple_embedding
import state

# ── setup ─────────────────────────────────────────────────
FRAME_W, FRAME_H = 640, 480

detector   = FaceMeshDetector()
aggregator = ScoreAggregator(max_buffer=30)
identifier = FaceIdentifier(similarity_threshold=0.92)


def open_camera():
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
state.set_session(1)
print("Session started. Press Ctrl+C to quit.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera read failed. Reopening...")
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

                # ── identify who this face is ──────────────
                embedding  = compute_simple_embedding(landmarks)
                student_id = identifier.identify(embedding)

                # ── head pose ──────────────────────────────
                pose = estimate_head_pose(landmarks, FRAME_W, FRAME_H)
                if pose is None:
                    continue
                yaw, pitch = pose

                # ── eye aspect ratio ───────────────────────
                _, _, avg_ear = get_ear(landmarks)
                if avg_ear is None:
                    continue

                # ── attention score ────────────────────────
                score = compute_attention_score(yaw, pitch, avg_ear)
                frame_scores[student_id] = score

                # ── update Redis ───────────────────────────
                state.update(
                    student_id=student_id,
                    score=score,
                    yaw=yaw,
                    pitch=pitch,
                    ear=avg_ear,
                )

                # ── draw on frame ──────────────────────────
                nose_x, nose_y, _ = landmarks[1]
                color = (int(255 * (1 - score)), int(255 * score), 0)

                cv2.putText(frame, f"{student_id}",
                            (nose_x - 40, nose_y - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, f"Score: {score:.2f}",
                            (nose_x - 40, nose_y - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                cv2.putText(frame, f"y:{yaw:.0f} p:{pitch:.0f} e:{avg_ear:.2f}",
                            (nose_x - 40, nose_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # ── aggregator ─────────────────────────────────────
        aggregator.add_frame_scores(frame_scores)
        averages  = aggregator.get_all_averages()
        class_avg = aggregator.get_class_average()

        if averages:
            print("Rolling averages:")
            for sid, avg in averages.items():
                print(f"  yaw={yaw:.1f} pitch={pitch:.1f} ear={avg_ear:.3f} score={score:.4f}")
                print(f"  {sid}: {avg:.4f}")
            if class_avg:
                print(f"  Class avg: {class_avg:.4f}\n")

        # ── overlays ───────────────────────────────────────
        if class_avg is not None:
            cv2.putText(frame, f"Class avg: {class_avg:.2f}",
                        (10, FRAME_H - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (255, 255, 0), 2)

        cv2.putText(frame, f"Tracked: {identifier.get_enrolled_count()} face(s)",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2)

        cv2.imshow("Attention Tracker", frame)
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