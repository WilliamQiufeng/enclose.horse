import puzzle_model as pm
from z3 import Int, Bool, Optimize, If, Sum, PbLe, Implies, And, Or, BoolRef, ArithRef, sat
from dataclasses import dataclass

@dataclass
class Vector2iRef:
    x: ArithRef
    y: ArithRef

@dataclass
class Constraints:
    walls: list[list[BoolRef]]
    score: ArithRef
    constraints: list[BoolRef]


def build(puzzle: pm.Puzzle) -> Constraints:
    constraints = []
    score = Int("score")
    walls = [[Bool(f"wall_{r}_{c}") for c in range(puzzle.width)] for r in range(puzzle.height)]
    # reachable[r][c] is true iff the cell at (c, r) is reachable from the horse's starting position without crossing any walls or water
    reachable = [[Bool(f"reachable_{r}_{c}") for c in range(puzzle.width)] for r in range(puzzle.height)]

    # Number of walls must be <= budget
    constraints.append(PbLe([(walls[r][c], 1) for r in range(puzzle.height) for c in range(puzzle.width)], puzzle.budget))

    # Walls can only be placed on grass cells
    for y in range(puzzle.height):
        for x in range(puzzle.width):
            if puzzle.get_cell(x, y) != pm.CellType.GRASS:
                constraints.append(walls[y][x] == False)

    # A cell is reachable if it's not a wall or water, and at least one of its neighbors is reachable
    for y in range(puzzle.height):
        for x in range(puzzle.width):
            cell = puzzle.get_cell(x, y)
            match cell:
                case pm.CellType.HORSE:
                    # The horse's starting position is reachable
                    constraints.append(reachable[y][x] == True)
                case pm.CellType.WATER:
                    constraints.append(reachable[y][x] == False)
                case _:
                    # Adjacent cells that are reachable
                    neighbor_reachable = []
                    if y > 0:
                        neighbor_reachable.append(reachable[y-1][x])
                    if y < puzzle.height - 1:
                        neighbor_reachable.append(reachable[y+1][x])
                    if x > 0:
                        neighbor_reachable.append(reachable[y][x-1])
                    if x < puzzle.width - 1:
                        neighbor_reachable.append(reachable[y][x+1])
                    # If the cell is a portal, also consider the paired portal cell as a neighbor
                    if cell == pm.CellType.PORTAL:
                        portal_exit = puzzle.portals[pm.Vector2i(x, y)]
                        neighbor_reachable.append(reachable[portal_exit.y][portal_exit.x])
                    constraints.append(reachable[y][x] == And(walls[y][x] == False, Or(neighbor_reachable)))
                    

    # The horse must not be able to reach the boundaries of the grid (enclosure condition)
    for y in range(puzzle.height):
        constraints.append(reachable[y][0] == False)
        constraints.append(reachable[y][puzzle.width - 1] == False)
    for x in range(puzzle.width):
        constraints.append(reachable[0][x] == False)
        constraints.append(reachable[puzzle.height - 1][x] == False)
    
    # Score is the sum of bonuses + area in reachable cells
    score_terms = []
    for y in range(puzzle.height):
        for x in range(puzzle.width):
            cell = puzzle.get_cell(x, y)
            match cell:
                case pm.CellType.GRASS | pm.CellType.PORTAL | pm.CellType.HORSE:
                    score_terms.append(If(reachable[y][x], 1, 0))
                case pm.CellType.BONUS:
                    score_terms.append(If(reachable[y][x], puzzle.bonuses[pm.Vector2i(x, y)] + 1, 0))
            # Account for wall cost in score if applicable
            if puzzle.wall_cost != 0:
                score_terms.append(If(walls[y][x], -puzzle.wall_cost, 0))

    constraints.append(score == Sum(score_terms))
    return Constraints(walls=walls, score=score, constraints=constraints)

def model_to_solution(puzzle: pm.Puzzle, model) -> pm.PuzzleSolution:
    walls = []
    score = model.evaluate(Int("score")).as_long()
    for y in range(puzzle.height):
        for x in range(puzzle.width):
            if model.evaluate(Bool(f"wall_{y}_{x}")):
                walls.append(pm.Vector2i(x, y))
    return pm.PuzzleSolution(puzzle=puzzle, walls=walls, score=score)

def solve(puzzle: pm.Puzzle) -> pm.PuzzleSolution | None:
    constraints = build(puzzle)
    s = Optimize()
    s.add(constraints.constraints)
    s.maximize(constraints.score)
    if s.check() == sat:
        m = s.model()
        solution = model_to_solution(puzzle, m)
        return solution
    else:
        return None