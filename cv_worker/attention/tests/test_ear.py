import cv2
from facemesh import FaceMeshDetector
from ear import get_ear

detector = FaceMeshDetector()
cap = cv2.VideoCapture("http://192.168.1.102:4747/video")  

# EAR below this = eyes considered closed
EAR_THRESHOLD = 0.2

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = detector.process(frame)

    if results:
        all_landmarks = detector.get_landmarks_array(results, frame.shape)

        for i, landmarks in enumerate(all_landmarks):
            left_ear, right_ear, avg_ear = get_ear(landmarks)

            if avg_ear is not None:
                status = "EYES OPEN" if avg_ear > EAR_THRESHOLD else "EYES CLOSED"
                color  = (0, 255, 0) if avg_ear > EAR_THRESHOLD else (0, 0, 255)

                print(f"Face {i+1} → Left: {left_ear:.3f}  "
                      f"Right: {right_ear:.3f}  "
                      f"Avg: {avg_ear:.3f}  {status}")

                cv2.putText(
                    frame,
                    f"EAR: {avg_ear:.3f} - {status}",
                    (10, 30 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, color, 2
                )

    cv2.imshow("EAR Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.close()