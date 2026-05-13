from typing import Optional


# thresholds
EAR_THRESHOLD  = 0.12
YAW_MAX        = 60.0
PITCH_MAX      = 40.0
DROWSY_PENALTY = 0.5
YAW_OFFSET     = -18.0   # calibrate to your camera angle
PITCH_OFFSET   = 0.0


def compute_attention_score(
    yaw: float,
    pitch: float,
    ear: float,
) -> float:
    # correct for camera angle
    corrected_yaw   = yaw - YAW_OFFSET
    corrected_pitch = pitch - PITCH_OFFSET

    head_score = 1.0 - (abs(corrected_yaw) / YAW_MAX) - (abs(corrected_pitch) / PITCH_MAX)
    head_score = max(0.0, min(1.0, head_score))

    eye_multiplier = 1.0 if ear > EAR_THRESHOLD else DROWSY_PENALTY

    score = head_score * eye_multiplier
    return round(score, 4)


def compute_class_attention(scores: list[float]) -> Optional[float]:
    """
    Averages attention scores across all detected students in a frame.
    Returns None if no students detected.
    Used by the alert system to check if class attention drops too low.
    """
    if not scores:
        return None

    return round(sum(scores) / len(scores), 4)