import cv2
from facemesh import FaceMeshDetector
from head_pose import estimate_head_pose

detector = FaceMeshDetector()
cap = cv2.VideoCapture("http://192.168.1.102:4747/video")

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = detector.process(frame)

    if results:
        all_landmarks = detector.get_landmarks_array(results, frame.shape)
        h, w, _ = frame.shape

        for i, landmarks in enumerate(all_landmarks):
            pose = estimate_head_pose(landmarks, w, h)
            if pose:
                yaw, pitch = pose
                print(f"Face {i+1} → Yaw: {yaw:+.1f}°  Pitch: {pitch:+.1f}°")

                # draw on frame
                cv2.putText(
                    frame,
                    f"Yaw: {yaw:+.1f}  Pitch: {pitch:+.1f}",
                    (10, 30 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2
                )

    cv2.imshow("Head Pose", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.close()