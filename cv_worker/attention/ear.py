import numpy as np
from typing import Tuple, Optional


# MediaPipe landmark indexes for each eye
# order: [p1, p2, p3, p4, p5, p6]
LEFT_EYE_INDEXES  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDEXES = [33,  160, 158, 133, 153, 144]


def _euclidean(p1: tuple, p2: tuple) -> float:
    """Distance between two (x, y) points."""
    return np.linalg.norm(
        np.array([p1[0], p1[1]]) - np.array([p2[0], p2[1]])
    )


def compute_ear(eye_landmarks: list) -> float:
    """
    Takes 6 (x, y, z) points for one eye in order [p1..p6].
    Returns the EAR value for that eye.
    """
    p1, p2, p3, p4, p5, p6 = eye_landmarks

    vertical_1   = _euclidean(p2, p6)   # top-left  to bottom-left
    vertical_2   = _euclidean(p3, p5)   # top-right to bottom-right
    horizontal   = _euclidean(p1, p4)   # left corner to right corner

    if horizontal == 0:
        return 0.0

    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return float(ear)


def get_ear(
    landmarks: list,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Takes full list of 478 landmarks for one face.
    Returns (left_ear, right_ear, avg_ear).
    Returns (None, None, None) if landmarks are missing.
    """
    try:
        left_eye_landmarks = [landmarks[i] for i in LEFT_EYE_INDEXES]
        right_eye_landmarks = [landmarks[i] for i in RIGHT_EYE_INDEXES]
    except IndexError:
        return None, None, None

    left_ear  = compute_ear(left_eye_landmarks)
    right_ear = compute_ear(right_eye_landmarks)
    avg_ear   = (left_ear + right_ear) / 2.0

    return left_ear, right_ear, avg_ear