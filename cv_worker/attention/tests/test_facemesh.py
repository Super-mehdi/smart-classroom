import cv2
from facemesh import FaceMeshDetector

detector = FaceMeshDetector()
cap = cv2.VideoCapture("http://192.168.1.102:4747/video")  

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = detector.process(frame)

    if results:
        landmarks_per_face = detector.get_landmarks_array(results, frame.shape)
        print(f"Detected {len(landmarks_per_face)} face(s), "
              f"{len(landmarks_per_face[0])} landmarks each")

    cv2.imshow("FaceMesh Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.close()