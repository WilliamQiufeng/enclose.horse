import puzzle_model as pm
from dataclasses import dataclass

@dataclass(frozen=True)
class AsciiParseResult:
    cells: list[list[pm.CellType]]
    special_chars: dict[str, list[pm.Vector2i]]
    remaining_lines: list[str]

def read_ascii(lines: list[str], height: int) -> AsciiParseResult:
    # read height amount of lines, returning result of parsing
    cells: list[list[pm.CellType]] = []
    special_chars: dict[str, list[pm.Vector2i]] = {}
    for y in range(height):
        line = lines[y].rstrip('\n')
        row = []
        for x, char in enumerate(line):
            match char:
                case '.':
                    row.append(pm.CellType.GRASS)
                case '~':
                    row.append(pm.CellType.WATER)
                case 'H':
                    row.append(pm.CellType.HORSE)
                case c:
                    # c is a bonus character, we can have multiple bonuses with the same character, so we store them in a list
                    row.append(pm.CellType.BONUS)
                    if c not in special_chars:
                        special_chars[c] = []
                    special_chars[c].append(pm.Vector2i(x, y))
        cells.append(row)
    return AsciiParseResult(cells=cells, special_chars=special_chars, remaining_lines=lines[height:])

def from_lines(lines: list[str]) -> pm.Puzzle:
    remaining_lines = lines

    width = 0
    height = 0
    budget = 0
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
                bonus_positions = ascii_result.special_chars
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
                    case ["portal", c]:
                        if c not in bonus_positions:
                            raise ValueError(f"Portal character {c} not found in map.")
                        positions = bonus_positions[c]
                        if len(positions) != 2:
                            raise ValueError(f"Portal character {c} must appear exactly twice in the map.")
                        portals[positions[0]] = positions[1]
                        portals[positions[1]] = positions[0]
                        set_cell(positions[0].x, positions[0].y, pm.CellType.PORTAL)
                        set_cell(positions[1].x, positions[1].y, pm.CellType.PORTAL)
                    case ["bonus", c, b]:
                        if c not in bonus_positions:
                            raise ValueError(f"Bonus character {c} not found in map.")
                        for pos in bonus_positions[c]:
                            set_cell(pos.x, pos.y, pm.CellType.BONUS)
                            bonuses[pos] = int(b)
                    case _:
                        raise ValueError(f"Unknown directive {line}")
                remaining_lines = rest
    return pm.Puzzle(width=width, height=height, budget=budget, cells=cells, bonuses=bonuses, portals=portals)