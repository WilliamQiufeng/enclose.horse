import puzzle_model as pm

def from_lines(lines: list[str]) -> pm.Puzzle:
    width = 0
    height = 0
    budget = 0
    horse = pm.Vector2i(0, 0)
    cells: list[list[pm.CellType]] = []
    bonuses = {}
    portals = {}

    def set_cell(x: int, y: int, cell_type: pm.CellType):
        cells[y][x] = cell_type

    for line in lines:
        words = line.split()
        match words:
            case ["grid", w, h]:
                width = int(w)
                height = int(h)
                cells = [[pm.CellType.GRASS for _ in range(width)] for _ in range(height)]
            case ["budget", b]:
                budget = int(b)
            case ["horse", x, y]:
                set_cell(int(x), int(y), pm.CellType.HORSE)
                horse = pm.Vector2i(int(x), int(y))
            case ["water", x, y]:
                set_cell(int(x), int(y), pm.CellType.WATER)
            case ["portal", x1, y1, x2, y2]:
                set_cell(int(x1), int(y1), pm.CellType.PORTAL)
                set_cell(int(x2), int(y2), pm.CellType.PORTAL)
                portals[pm.Vector2i(int(x1), int(y1))] = pm.Vector2i(int(x2), int(y2))
                portals[pm.Vector2i(int(x2), int(y2))] = pm.Vector2i(int(x1), int(y1))
            case ["bonus", x, y, b]:
                set_cell(int(x), int(y), pm.CellType.BONUS)
                bonuses[pm.Vector2i(int(x), int(y))] = int(b)
    return pm.Puzzle(width=width, height=height, budget=budget, cells=cells, bonuses=bonuses, portals=portals, horse=horse)