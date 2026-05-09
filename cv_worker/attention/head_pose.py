import cv2
import numpy as np
from typing import Tuple, Optional


# 3D coordinates of the 6 landmarks on a generic human face (in mm)
# these are fixed reference points — same for every person
MODEL_POINTS = np.array([
    (0.0,    0.0,    0.0),     # nose tip
    (0.0,   -63.6, -12.5),    # chin
    (-43.3,  32.7, -26.0),    # left eye corner
    (43.3,   32.7, -26.0),    # right eye corner
    (-28.9, -28.9, -24.1),    # left mouth corner
    (28.9,  -28.9, -24.1),    # right mouth corner
], dtype=np.float64)

# MediaPipe landmark indexes for the 6 points above
LANDMARK_INDEXES = [1, 152, 263, 33, 287, 57]


def get_camera_matrix(frame_w: int, frame_h: int) -> np.ndarray:
    """
    Estimate camera intrinsics from frame size.
    Focal length is approximated as frame width (good enough for webcams).
    """
    focal_length = frame_w
    center = (frame_w / 2, frame_h / 2)
    return np.array([
        [focal_length, 0,            center[0]],
        [0,            focal_length, center[1]],
        [0,            0,            1         ],
    ], dtype=np.float64)


def estimate_head_pose(
    landmarks: list,
    frame_w: int,
    frame_h: int,
) -> Optional[Tuple[float, float]]:
    """
    Takes a list of 478 (x, y, z) landmarks for one face.
    Returns (yaw, pitch) in degrees, or None if estimation fails.

    yaw   > 0 → looking right,  < 0 → looking left
    pitch > 0 → looking down,   < 0 → looking up
    """

    # extract the 6 key landmark 2D positions (x, y only)
    image_points = np.array([
        [landmarks[i][0], landmarks[i][1]]
        for i in LANDMARK_INDEXES
    ], dtype=np.float64)

    camera_matrix = get_camera_matrix(frame_w, frame_h)

    # no lens distortion assumed (good enough for attention tracking)
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    success, rotation_vec, translation_vec = cv2.solvePnP(
        MODEL_POINTS,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )

    if not success:
        return None

    # convert rotation vector to rotation matrix
    rotation_matrix, _ = cv2.Rodrigues(rotation_vec)

    # decompose rotation matrix into euler angles
    proj_matrix = np.hstack((rotation_matrix, translation_vec))
    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)

    pitch = euler_angles[0][0]
    yaw   = euler_angles[1][0]

    # normalize angles to [-90, 90] range
    pitch = float(np.clip(pitch, -90, 90))
    yaw   = float(np.clip(yaw,   -90, 90))

    return yaw, pitch