import layout
from pacman import GameState
from problems.q1b_problem import q1b_problem
from solvers.q1b_solver import astar_initialise, astar_loop_body
import itertools

def load_test_gamestate(layout_name, num_ghosts=0):
    lay = layout.getLayout(layout_name)
    game_state = GameState()
    game_state.initialize(lay, num_ghosts)
    return game_state

def run_once(gameState, weight, patience, time_limit=9.0):
    problem = q1b_problem(gameState)
    astarData = astar_initialise(problem)
    astarData.weight = weight
    astarData.patience = patience
    num_expansions = 0
    terminate = False
    while not terminate:
        num_expansions += 1
        terminate, result = astar_loop_body(problem, astarData)
    return num_expansions, astarData.highest_score

test_layouts = ["q1b_bigCorners", "q1b_mediumCorners", "q1b_openCorners", "q1b_smallCorners", "q1b_tinyCorners", "q1b_trickyCorners"]

weights = [1.0, 1.5, 2.0, 3.0, 5.0]
patiences = [20, 50, 100, 200]

for layout_name in test_layouts:
    gameState = load_test_gamestate(layout_name)
    print(f"--- layout: {layout_name} ---")
    for w, p in itertools.product(weights, patiences):
        exp, score = run_once(gameState, w, p)
        print(f"weight={w:<5} patience={p:<6} expansions={exp:<8} score={score}")