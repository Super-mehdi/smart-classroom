from typing import Optional


# thresholds
EAR_THRESHOLD  = 0.2   # below this = eyes closed
YAW_MAX        = 45.0  # degrees — full yaw penalty at this angle
PITCH_MAX      = 30.0  # degrees — full pitch penalty at this angle
DROWSY_PENALTY = 0.3   # multiplier when eyes are closed


def compute_attention_score(
    yaw: float,
    pitch: float,
    ear: float,
) -> float:
    """
    Computes attention score for a single student in a single frame.

    Args:
        yaw:   head rotation left/right in degrees
        pitch: head rotation up/down in degrees
        ear:   average eye aspect ratio (both eyes)

    Returns:
        float between 0.0 (not attentive) and 1.0 (fully attentive)
    """

    # part 1 — head direction score
    head_score = 1.0 - (abs(yaw) / YAW_MAX) - (abs(pitch) / PITCH_MAX)

    # clamp to [0.0, 1.0] — can't go negative or above 1
    head_score = max(0.0, min(1.0, head_score))

    # part 2 — drowsiness multiplier
    eye_multiplier = 1.0 if ear > EAR_THRESHOLD else DROWSY_PENALTY

    # final score
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