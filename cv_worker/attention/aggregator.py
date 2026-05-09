from collections import defaultdict
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class StudentScoreBuffer:
    """Keeps a rolling buffer of recent scores for one student."""
    student_id: str
    scores: list[float] = field(default_factory=list)
    max_buffer: int = 30   # keep last 30 frames (~5 seconds at 6fps)

    def add_score(self, score: float):
        self.scores.append(score)
        if len(self.scores) > self.max_buffer:
            self.scores.pop(0)

    def average(self) -> Optional[float]:
        if not self.scores:
            return None
        return round(sum(self.scores) / len(self.scores), 4)


class ScoreAggregator:
    """
    Receives per-frame attention scores per student
    and maintains a rolling average per student.
    """

    def __init__(self, max_buffer: int = 30):
        self.max_buffer = max_buffer
        self._buffers: dict[str, StudentScoreBuffer] = {}

    def add_frame_scores(self, scores: dict[str, float]):
        """
        scores = {"S001": 0.85, "S042": 0.32, ...}
        Call this once per frame with all detected students.
        """
        for student_id, score in scores.items():
            if student_id not in self._buffers:
                self._buffers[student_id] = StudentScoreBuffer(
                    student_id=student_id,
                    max_buffer=self.max_buffer,
                )
            self._buffers[student_id].add_score(score)

    def get_student_average(self, student_id: str) -> Optional[float]:
        """Returns the rolling average score for one student."""
        buf = self._buffers.get(student_id)
        if buf is None:
            return None
        return buf.average()

    def get_all_averages(self) -> dict[str, float]:
        """Returns rolling averages for all students seen so far."""
        return {
            sid: buf.average()
            for sid, buf in self._buffers.items()
            if buf.average() is not None
        }

    def get_class_average(self) -> Optional[float]:
        """Returns the average score across all students."""
        averages = list(self.get_all_averages().values())
        if not averages:
            return None
        return round(sum(averages) / len(averages), 4)

    def reset(self):
        """Clear all buffers — call when a session ends."""
        self._buffers.clear()