import numpy as np
from typing import Optional


def compute_simple_embedding(landmarks: list) -> np.ndarray:
    """
    Computes a simple face embedding from landmarks.
    Normalized relative to face center and size.
    """
    key_indexes = [
        1, 152, 263, 33, 287, 57, 168, 6,
        197, 195, 5, 4, 75, 305, 159, 145,
        386, 374, 0, 17,
    ]

    points = np.array([
        [landmarks[i][0], landmarks[i][1]]
        for i in key_indexes
    ], dtype=np.float32)

    center = points.mean(axis=0)
    points -= center
    scale  = np.abs(points).max()
    if scale > 0:
        points /= scale

    return points.flatten()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class FaceIdentifier:
    def __init__(self, similarity_threshold: float = 0.80): 
        self.threshold = similarity_threshold
        self._known: dict[str, np.ndarray] = {}
        self._auto_id_counter = 0

    def enroll(self, student_id: str, embedding: np.ndarray):
        self._known[student_id] = embedding

    def identify(self, embedding: np.ndarray) -> str:
        best_match = None
        best_score = 0.0

        for student_id, known_emb in self._known.items():
            score = cosine_similarity(embedding, known_emb)
            if score > best_score:
                best_score = score
                best_match = student_id

        if best_match and best_score >= self.threshold:
            return best_match

        self._auto_id_counter += 1
        new_id = f"FACE_{self._auto_id_counter:03d}"
        self._known[new_id] = embedding
        print(f"New face enrolled: {new_id}")
        return new_id

    def get_enrolled_count(self) -> int:
        return len(self._known)