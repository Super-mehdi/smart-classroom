import cv2
from facemesh import FaceMeshDetector
from head_pose import estimate_head_pose
from ear import get_ear
from attention_score import compute_attention_score, compute_class_attention

detector = FaceMeshDetector()
cap = cv2.VideoCapture("http://192.168.1.102:4747/video")  

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = detector.process(frame)
    frame_scores = []

    if results:
        all_landmarks = detector.get_landmarks_array(results, frame.shape)
        h, w, _ = frame.shape

        for i, landmarks in enumerate(all_landmarks):

            # get yaw and pitch
            pose = estimate_head_pose(landmarks, w, h)
            if pose is None:
                continue
            yaw, pitch = pose

            # get EAR
            _, _, avg_ear = get_ear(landmarks)
            if avg_ear is None:
                continue

            # compute attention score
            score = compute_attention_score(yaw, pitch, avg_ear)
            frame_scores.append(score)

            # color: green = attentive, red = not attentive
            color = (
                int(255 * (1 - score)),  # red channel
                int(255 * score),        # green channel
                0
            )

            print(f"Face {i+1} → "
                  f"Yaw: {yaw:+.1f}°  "
                  f"Pitch: {pitch:+.1f}°  "
                  f"EAR: {avg_ear:.3f}  "
                  f"Score: {score:.4f}")

            cv2.putText(
                frame,
                f"Score: {score:.2f}",
                (10, 30 + i * 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, color, 2
            )

    # class average
    class_avg = compute_class_attention(frame_scores)
    if class_avg is not None:
        print(f"Class avg → {class_avg:.4f}\n")
        cv2.putText(
            frame,
            f"Class avg: {class_avg:.2f}",
            (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (255, 255, 0), 2
        )

    cv2.imshow("Attention Score", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.close()