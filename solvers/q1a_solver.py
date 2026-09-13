#---------------------#
# DO NOT MODIFY BEGIN #
#---------------------#

import logging

import util
from problems.q1a_problem import q1a_problem

#-------------------#
# DO NOT MODIFY END #
#-------------------#

def q1a_solver(problem: q1a_problem):
    astarData = astar_initialise(problem)
    num_expansions = 0
    terminate = False
    while not terminate:
        num_expansions += 1
        terminate, result = astar_loop_body(problem, astarData)
    print(f'Number of node expansions: {num_expansions}')
    return result

class AStarData:
    # YOUR CODE HERE
    def __init__(self):
        self.frontier = util.PriorityQueue()
        self.explored = set()
        self.goal = None

def astar_initialise(problem: q1a_problem):
    # YOUR CODE HERE
    astarData = AStarData()
    g_val = 0   # g(n) = 0 initially
    start_state = problem.getStartState()   # Get the starting point of Pac Man
    food_loc = problem.startingGameState.getFood()   # Find the food location
    astarData.goal = food_loc.asList()[0]
    source = (start_state, [], g_val)
    h_val = astar_heuristic(start_state, astarData.goal)    # Compute h(n)
    astarData.frontier.push(source, g_val + h_val)
    return astarData

def astar_loop_body(problem: q1a_problem, astarData: AStarData):
    # YOUR CODE HERE
    if astarData.frontier.isEmpty():
        return True, []

    curr_state, path, g_val = astarData.frontier.pop()   # Extract current node

    if problem.isGoalState(curr_state):   # Check if reach the goal
        return True, path

    if curr_state not in astarData.explored:
        astarData.explored.add(curr_state)

        for next_state, action, step_cost in problem.getSuccessors(curr_state):   # Get all next possible state, action, and cost
            new_g = g_val + step_cost
            new_path = path + [action]
            h_val = astar_heuristic(next_state, astarData.goal)   # Re-calculate new h(n) from next_state to goal
            f_val = new_g + h_val
            node = (next_state, new_path, new_g)
            astarData.frontier.push(node, f_val)

    return False, None

def astar_heuristic(current, goal):
    # YOUR CODE HERE
    if current is None or goal is None:
        return 0

    return util.manhattanDistance(current, goal)
