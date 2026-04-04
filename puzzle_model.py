from dataclasses import dataclass
from enum import Enum, auto

class CellType(Enum):
    GRASS = 0
    WATER = auto()
    HORSE = auto()
    PORTAL = auto()
    BONUS = auto()

@dataclass(frozen=True)
class Vector2i:
    x: int
    y: int

@dataclass(frozen=True)
class Puzzle:
    width: int
    height: int
    budget: int
    cells: list[list[CellType]]
    bonuses: dict[Vector2i, int]
    portals: dict[Vector2i, Vector2i]
    horse: Vector2i

    def get_cell(self, x: int, y: int) -> CellType:
        return self.cells[y][x]

    def get_cell_vec(self, pos: Vector2i) -> CellType:
        return self.get_cell(pos.x, pos.y)

@dataclass(frozen=True)
class PuzzleSolution:
    puzzle: Puzzle
    walls: list[Vector2i]
    score: int