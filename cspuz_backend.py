import puzzle_model as pm
import cspuz as cp
import cspuz.graph as cspgraph
from typing import Generator
from functools import reduce

def neighbors(puzzle: pm.Puzzle, x: int, y: int) -> Generator[pm.Vector2i, None, None]:
    if y > 0:
        yield pm.Vector2i(x, y-1)
    if y < puzzle.height - 1:
        yield pm.Vector2i(x, y+1)
    if x > 0:
        yield pm.Vector2i(x-1, y)
    if x < puzzle.width - 1:
        yield pm.Vector2i(x+1, y)

def lex_less(v1: pm.Vector2i, v2: pm.Vector2i) -> bool:
    return v1.x < v2.x or (v1.x == v2.x and v1.y < v2.y)

def solve_for(puzzle: pm.Puzzle, minimum_score: int) -> pm.PuzzleSolution | None:
    solver = cp.Solver()
    reachable = solver.bool_array((puzzle.height, puzzle.width))
    walls = solver.bool_array((puzzle.height, puzzle.width))
    score_terms = []

    # Construct connectivity graph
    graph = cspgraph.Graph(puzzle.width * puzzle.height)
    def add_edge(v1: pm.Vector2i, v2: pm.Vector2i):
        if lex_less(v1, v2):
            graph.add_edge(v1.y * puzzle.width + v1.x, v2.y * puzzle.width + v2.x)
    for y in range(puzzle.height):
        for x in range(puzzle.width):
            cell = puzzle.get_cell(x, y)
            if cell == pm.CellType.WATER:
                continue
            
            terms = []
            for neighbor in neighbors(puzzle, x, y):
                neighbor_cell = puzzle.get_cell_vec(neighbor)
                if neighbor_cell == pm.CellType.WATER:
                    continue
                # Add edge in connectivity graph
                add_edge(pm.Vector2i(x, y), neighbor)
                terms.append(reachable[neighbor.y, neighbor.x])
            
            if cell == pm.CellType.PORTAL:
                portal_exit = puzzle.portals[pm.Vector2i(x, y)]
                add_edge(pm.Vector2i(x, y), portal_exit)
                terms.append(reachable[portal_exit.y, portal_exit.x])
            
            # A cell is reachable if it is not a wall and at least one of its neighbors is reachable
            solver.ensure(~(cp.fold_or(terms) & ~walls[y, x]) | reachable[y, x])

    for y in range(puzzle.height):
        for x in range(puzzle.width):
            if x == 0 or x == puzzle.width - 1 or y == 0 or y == puzzle.height - 1:
                # Boundary cells must not be reachable
                solver.ensure(~reachable[y, x])
            cell = puzzle.get_cell(x, y)
            match cell:
                case pm.CellType.HORSE:
                    # Horses are reachable
                    solver.ensure(reachable[y, x])
                case pm.CellType.WATER | pm.CellType.BONUS | pm.CellType.PORTAL:
                    # Cannot place walls there
                    solver.ensure(~walls[y, x])

            # Add scores to reachable cells        
            match cell:
                case pm.CellType.GRASS | pm.CellType.PORTAL | pm.CellType.HORSE:
                    score_terms.append(reachable[y, x].cond(1, 0))
                case pm.CellType.BONUS:
                    score_terms.append(reachable[y, x].cond(puzzle.bonuses[pm.Vector2i(x, y)] + 1, 0))

    # add reachability constraints
    cp.graph.active_vertices_connected(solver, reachable.flatten(), graph=graph)

    # Require minimum score
    score = solver.int_var(minimum_score, minimum_score + 500)

    # Account for wall cost in score if applicable
    if puzzle.wall_cost != 0:
        for wall in walls.flatten():
            score_terms.append(wall.cond(-puzzle.wall_cost, 0))

    solver.ensure(score == reduce(lambda a, b: a + b, score_terms))
    solver.ensure(score >= minimum_score)

    # Budget requirement
    solver.ensure(cp.count_true(*walls.flatten()) <= puzzle.budget)

    result = solver.find_answer()

    if not result:
        return None
    
    solution_score = score.sol
    solution_walls = []
    for y in range(puzzle.height):
        for x in range(puzzle.width):
            if walls[y, x].sol:
                solution_walls.append(pm.Vector2i(x, y))

    return pm.PuzzleSolution(puzzle=puzzle, walls=solution_walls, score=solution_score)

def solve(puzzle: pm.Puzzle, minimum_score: int = -500, maximum_score: int = 500) -> pm.PuzzleSolution | None:
    # Binary search for optimal score
    # Find the maximum score for which there is a solution
    low = minimum_score
    high = maximum_score
    best_solution = None
    while low <= high:
        mid = (low + high) // 2
        solution = solve_for(puzzle, mid)
        if solution is not None:
            best_solution = solution
            # We can use a score higher than mid
            low = solution.score + 1
        else:
            high = mid - 1
    return best_solution

