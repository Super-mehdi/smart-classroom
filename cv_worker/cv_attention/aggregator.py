from collections import defaultdict
from typing import Optional
from dataclasses import dataclass, field
import time


@dataclass
class StudentScoreBuffer:
    student_id: str
    scores: list[float] = field(default_factory=list)
    max_buffer: int = 30
    last_seen: float = field(default_factory=time.time)  # NEW

    def add_score(self, score: float):
        self.scores.append(score)
        self.last_seen = time.time()  # NEW
        if len(self.scores) > self.max_buffer:
            self.scores.pop(0)

    def average(self) -> Optional[float]:
        if not self.scores:
            return None
        return round(sum(self.scores) / len(self.scores), 4)


class ScoreAggregator:
    def __init__(self, max_buffer: int = 30, stale_timeout: float = 5.0):
        self.max_buffer   = max_buffer
        self.stale_timeout = stale_timeout  # NEW — remove after 5s unseen
        self._buffers: dict[str, StudentScoreBuffer] = {}

    def add_frame_scores(self, scores: dict[str, float]):
        for student_id, score in scores.items():
            if student_id not in self._buffers:
                self._buffers[student_id] = StudentScoreBuffer(
                    student_id=student_id,
                    max_buffer=self.max_buffer,
                )
            self._buffers[student_id].add_score(score)

        # NEW — remove faces not seen recently
        now = time.time()
        stale = [
            sid for sid, buf in self._buffers.items()
            if now - buf.last_seen > self.stale_timeout
        ]
        for sid in stale:
            print(f"Removing stale face: {sid}")
            del self._buffers[sid]

    def get_student_average(self, student_id: str) -> Optional[float]:
        buf = self._buffers.get(student_id)
        if buf is None:
            return None
        return buf.average()

    def get_all_averages(self) -> dict[str, float]:
        return {
            sid: buf.average()
            for sid, buf in self._buffers.items()
            if buf.average() is not None
        }

    def get_class_average(self) -> Optional[float]:
        averages = list(self.get_all_averages().values())
        if not averages:
            return None
        return round(sum(averages) / len(averages), 4)

    def reset(self):
        self._buffers.clear()