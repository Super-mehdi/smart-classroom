from typing import Optional
from dataclasses import dataclass, field


@dataclass
class SeatGrid:
    """
    Defines the classroom seat layout and maps
    frame positions to student IDs.
    """
    rows: int
    cols: int
    frame_w: int
    frame_h: int

    # seat_map[row][col] = student_id or None if seat is empty
    seat_map: list[list[Optional[str]]] = field(default_factory=list)

    def __post_init__(self):
        if not self.seat_map:
            # initialize empty grid
            self.seat_map = [
                [None for _ in range(self.cols)]
                for _ in range(self.rows)
            ]

    def assign_student(self, row: int, col: int, student_id: str):
        """Assign a student ID to a seat."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.seat_map[row][col] = student_id

    def get_cell(self, x: int, y: int) -> Optional[tuple[int, int]]:
        """
        Given a pixel position (x, y) in the frame,
        returns the (row, col) of the seat it falls into.
        Returns None if out of bounds.
        """
        if x < 0 or x >= self.frame_w or y < 0 or y >= self.frame_h:
            return None

        cell_w = self.frame_w / self.cols
        cell_h = self.frame_h / self.rows

        col = int(x / cell_w)
        row = int(y / cell_h)

        # clamp to grid bounds
        col = min(col, self.cols - 1)
        row = min(row, self.rows - 1)

        return row, col

    def get_student_id(self, x: int, y: int) -> Optional[str]:
        """
        Given a pixel position, returns the student_id
        sitting in that seat, or None if seat is empty.
        """
        cell = self.get_cell(x, y)
        if cell is None:
            return None
        row, col = cell
        return self.seat_map[row][col]