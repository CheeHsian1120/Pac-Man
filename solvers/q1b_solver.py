#---------------------#
# DO NOT MODIFY BEGIN #
#---------------------#

import logging

import util
from problems.q1b_problem import q1b_problem

#-------------------#
# DO NOT MODIFY END #
#-------------------#

# Global caches
MST = {}
FOOD_DIST = {}

def q1b_solver(problem: q1b_problem):
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
        self.best_path = []
        self.highest_score = float('-inf')
        self.init_food_cnt = 0

def astar_initialise(problem: q1b_problem):
    # YOUR CODE HERE
    global MST, FOOD_DIST
    MST = {}
    FOOD_DIST = {}

    astarData = AStarData()
    g_val = 0
    start_state = problem.getStartState()
    astarData.init_food_cnt = len(start_state[1])
    astarData.highest_score = float('-inf')

    walls = problem.startingGameState.getWalls()
    width, height = walls.width, walls.height
    for food_loc in start_state[1]:  # Compute precompute table on every food dot
        FOOD_DIST[food_loc] = bfs(food_loc, walls, width, height)
    
    source = (start_state, [], g_val)
    astarData.frontier.push(source, 0)
    return astarData

def astar_loop_body(problem: q1b_problem, astarData: AStarData):
    # YOUR CODE HERE
    if astarData.frontier.isEmpty():  # Return the current best path if frontier is empty
        return True, astarData.best_path

    curr_state, path, g_val = astarData.frontier.pop()
    eaten_food = astarData.init_food_cnt - len(curr_state[1])
    curr_score = (eaten_food * 10) - g_val

    # Plus 500 marks if all food dots are fully consumed
    if problem.isGoalState(curr_state):
        curr_score += 500

    # Backup best result
    if curr_score > astarData.highest_score:
        astarData.highest_score = curr_score
        astarData.best_path = path

    # Skip if this state has been explored
    if curr_state in astarData.explored:
        return False, None

    if problem.isGoalState(curr_state):
        return True, astarData.best_path

    astarData.explored.add(curr_state)

    # Continue explore unseen location
    for next_state, action_list, step_cost in get_successors(curr_state, problem, k_limit=1):
        if next_state not in astarData.explored:
            new_g = g_val + step_cost
            new_path = path + action_list
            next_loc, next_foods = next_state
            h_val = astar_heuristic(next_loc, next_foods)
            f_val = new_g + (2.5 * h_val) - (new_g * 0.0001)  # Weighted A*
            node = (next_state, new_path, new_g)
            astarData.frontier.push(node, f_val)

    return False, None  # Did not find the goal, continue to the next iteration

def astar_heuristic(current, goals):
    # YOUR CODE HERE
    if not goals:
        return 0

    # Find the nearest food dot to consume
    closest_dist = min(FOOD_DIST[food_loc].get(current, float('inf')) for food_loc in goals)

    # Using Prim's algorithm to construct a minimum spanning tree
    # MST is helps to connect all food dots in a shortest way
    if goals not in MST:
        if len(goals) <= 1:
            MST[goals] = 0
        else:
            unvisited = set(goals)
            source = unvisited.pop()
            visited = {source}
            mst_cost = 0
            heap = util.PriorityQueue()

            for node in unvisited:
                dist = FOOD_DIST[source].get(node, float('inf'))
                heap.push((dist, node), dist)

            while unvisited and not heap.isEmpty():
                dist, curr_node = heap.pop()

                if curr_node in visited:
                    continue

                mst_cost += dist
                visited.add(curr_node)
                unvisited.remove(curr_node)

                for node in unvisited:
                    dist = FOOD_DIST[curr_node].get(node, float('inf'))
                    heap.push((dist, node), dist)
            
            MST[goals] = mst_cost

    return closest_dist + MST[goals]

def get_successors(state, problem, k_limit=1):
    """
    This function simulates the future state after consuming a single food dot.
    """
    current_loc, remaining_foods = state[0], state[1]
    successors = []
    walls = problem.startingGameState.getWalls()

    for curr_food in remaining_foods:
        # Get the required steps to reach that food dot
        step_cost = FOOD_DIST[curr_food].get(current_loc, float('inf'))  

        if step_cost == float('inf'):
            continue

        # Simulate the future state if eating this current food dot
        next_remaining_foods = remaining_foods - frozenset([curr_food])
        next_state = (curr_food, next_remaining_foods)

        # Get the required actions from current location to current target food
        action_list = backtracing(current_loc, curr_food, walls)

        successors.append((next_state, action_list, step_cost))

    # Sorting the successor states and return a nearest target
    successors.sort(key=lambda item: item[2])
    return successors[:k_limit]

def bfs(source, walls, width, height):
    """
    This Breadth-First Search precomputes for the game maze.
    Given a starting point, it computes all required distances to every grid in the maze.
    """
    dist = {source: 0}  # Record the distance from the starting point to any valid grid
    queue = util.Queue()
    queue.push(source)

    while not queue.isEmpty():
        x, y = queue.pop()

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy

            if 0 <= nx < width and 0 <= ny < height and not walls[nx][ny]:  # Checks the adjacent point in the maze and not the wall
                if (nx, ny) not in dist:
                    dist[(nx, ny)] = dist[(x, y)] + 1
                    queue.push((nx, ny))

    return dist

def backtracing(start, goal, walls):
    """
    This function utilizes the precomputes distances table, tracing the path from food dot to Pac Man in reverse.
    """
    path = []
    curr = start
    width, height = walls.width, walls.height
    
    dist_map = FOOD_DIST[goal]
    
    while curr != goal:
        x, y = curr
        current_dist = dist_map[(x, y)]
        
        directions_map = [
            (0, 1, 'North'),
            (0, -1, 'South'),
            (1, 0, 'East'),
            (-1, 0, 'West')
        ]
        
        for dx, dy, action in directions_map:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and not walls[nx][ny]:
                if dist_map.get((nx, ny)) == current_dist - 1:
                    path.append(action)
                    curr = (nx, ny)
                    break
                    
    return path