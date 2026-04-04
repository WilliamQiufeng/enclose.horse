from puzzle_model import *

cell_repr = {
    CellType.GRASS: '.',
    CellType.WATER: 'X',
    CellType.HORSE: 'H',
    CellType.PORTAL: '@',
    CellType.BONUS: 'B'
}

def repr_puzzle(puzzle: Puzzle) -> str:
    rows = []
    for y in range(puzzle.height):
        row = ''.join(cell_repr[puzzle.get_cell(x, y)] for x in range(puzzle.width))
        rows.append(row)
    return '\n'.join(rows)


def repr_solution(solution: PuzzleSolution) -> str:
    wall_set = set((wall.x, wall.y) for wall in solution.walls)
    rows = []
    for y in range(solution.puzzle.height):
        row = ''
        for x in range(solution.puzzle.width):
            if (x, y) in wall_set:
                row += '#'
            else:
                row += cell_repr[solution.puzzle.get_cell(x, y)]
        rows.append(row)
    return '\n'.join(rows)