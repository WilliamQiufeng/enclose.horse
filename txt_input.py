import puzzle_model as pm
from dataclasses import dataclass

@dataclass(frozen=True)
class AsciiParseResult:
    cells: list[list[pm.CellType]]
    horse: pm.Vector2i
    bonus_positions: dict[str, list[pm.Vector2i]]
    remaining_lines: list[str]

def read_ascii(lines: list[str], height: int) -> AsciiParseResult:
    # read height amount of lines, returning result of parsing
    cells: list[list[pm.CellType]] = []
    horse = pm.Vector2i(0, 0)
    bonus_positions: dict[str, list[pm.Vector2i]] = {}
    for y in range(height):
        line = lines[y].rstrip('\n')
        row = []
        for x, char in enumerate(line):
            match char:
                case '.':
                    row.append(pm.CellType.GRASS)
                case 'X':
                    row.append(pm.CellType.WATER)
                case 'H':
                    row.append(pm.CellType.HORSE)
                    horse = pm.Vector2i(x, y)
                case '@':
                    row.append(pm.CellType.PORTAL)
                case c:
                    # c is a bonus character, we can have multiple bonuses with the same character, so we store them in a list
                    row.append(pm.CellType.BONUS)
                    if c not in bonus_positions:
                        bonus_positions[c] = []
                    bonus_positions[c].append(pm.Vector2i(x, y))
        cells.append(row)
    return AsciiParseResult(cells=cells, horse=horse, bonus_positions=bonus_positions, remaining_lines=lines[height:])

def from_lines(lines: list[str]) -> pm.Puzzle:
    remaining_lines = lines

    width = 0
    height = 0
    budget = 0
    horse = pm.Vector2i(0, 0)
    cells: list[list[pm.CellType]] = []
    bonuses = {}
    bonus_positions: dict[str, list[pm.Vector2i]] = {}
    portals = {}

    def set_cell(x: int, y: int, cell_type: pm.CellType):
        cells[y][x] = cell_type

    while remaining_lines:
        match remaining_lines:
            case ["map", *rest]:
                ascii_result = read_ascii(rest, height)
                cells = ascii_result.cells
                horse = ascii_result.horse
                bonus_positions = ascii_result.bonus_positions
                remaining_lines = ascii_result.remaining_lines
            case [line, *rest]:
                words = line.split()
                match words:
                    case ["grid", w, h]:
                        width = int(w)
                        height = int(h)
                        cells = [[pm.CellType.GRASS for _ in range(width)] for _ in range(height)]
                    case ["budget", b]:
                        budget = int(b)
                    case ["portal", x1, y1, x2, y2]:
                        set_cell(int(x1), int(y1), pm.CellType.PORTAL)
                        set_cell(int(x2), int(y2), pm.CellType.PORTAL)
                        portals[pm.Vector2i(int(x1), int(y1))] = pm.Vector2i(int(x2), int(y2))
                        portals[pm.Vector2i(int(x2), int(y2))] = pm.Vector2i(int(x1), int(y1))
                    case ["bonus", c, b]:
                        if c not in bonus_positions:
                            raise ValueError(f"Bonus character {c} not found in map.")
                        for pos in bonus_positions[c]:
                            set_cell(pos.x, pos.y, pm.CellType.BONUS)
                            bonuses[pos] = int(b)
                    case _:
                        raise ValueError(f"Unknown directive {line}")
                remaining_lines = rest
    return pm.Puzzle(width=width, height=height, budget=budget, cells=cells, bonuses=bonuses, portals=portals, horse=horse)