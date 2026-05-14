import os
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# get the absolute path to the model file regardless of where you run from
MODEL_PATH = os.path.join(os.path.dirname(__file__), "face_landmarker.task")


class FaceMeshDetector:
    def __init__(
        self,
        max_num_faces: int = 40,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        base_options = python.BaseOptions(
            model_asset_path=MODEL_PATH    # ← absolute path now
        )
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=True,
            num_faces=max_num_faces,
            min_face_detection_confidence=min_detection_confidence,
            min_face_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def process(self, frame: np.ndarray) -> Optional[object]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )
        results = self.detector.detect(mp_image)

        if not results.face_landmarks:
            return None

        return results

    def get_landmarks_array(self, results, frame_shape: tuple) -> list:
        h, w, _ = frame_shape
        all_faces = []

        for face_landmarks in results.face_landmarks:
            landmarks = []
            for lm in face_landmarks:
                x = int(lm.x * w)
                y = int(lm.y * h)
                z = lm.z
                landmarks.append((x, y, z))
            all_faces.append(landmarks)

        return all_faces

    def close(self):
        self.detector.close()