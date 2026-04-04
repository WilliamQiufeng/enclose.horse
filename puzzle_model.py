from dataclasses import dataclass
from enum import Enum, auto

class CellType(Enum):
    GRASS = 0
    WATER = auto()
    HORSE = auto()
    PORTAL = auto()
    BONUS = auto()

@dataclass
class Vector2i:
    x: int
    y: int

@dataclass
class Puzzle:
    width: int
    height: int
    budget: int
    cells: list[CellType]
    bonuses: dict[Vector2i, int]
    portals: dict[Vector2i, Vector2i]

    def get_cell(self, x: int, y: int) -> CellType:
        return self.cells[y * self.width + x]

    def get_cell_vec(self, pos: Vector2i) -> CellType:
        return self.get_cell(pos.x, pos.y)

@dataclass
class PuzzleSolution:
    puzzle: Puzzle
    walls: list[Vector2i]