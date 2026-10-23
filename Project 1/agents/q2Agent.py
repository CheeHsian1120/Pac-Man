import logging
import random

import util
from game import Actions, Agent, Directions
from logs.search_logger import log_function
from pacman import GameState

ALL_PAIRS_CACHE = {}
MAP_INITIALIZED = False

def initialize_map_distances(gameState):
    """
    - This function precomputes the all-pairs shortest-path distances.
    - For every walkable position in the maze, run BFS once to find the shortest distance from that position to every other walkable position.
    - The result is stored in ALL_PAIRS_CACHE.
    """
    global MAP_INITIALIZED
    if MAP_INITIALIZED:
        return

    # Get the wall information in the maze
    walls = gameState.getWalls()
    width = walls.width
    height = walls.height

    # Find every walkable position
    valid_pos = []
    for x in range(width):
        for y in range(height):
            if not walls[x][y]:
                valid_pos.append((x, y))  # Add it if this position is not a wall

    # Breadth-First Search
    for start_pos in valid_pos:
        queue = util.Queue()
        queue.push((start_pos, 0))
        visited = {start_pos}
        ALL_PAIRS_CACHE[start_pos] = {start_pos: 0}  # Dictionary to store the distance from starting position to destination
        
        while not queue.isEmpty():
            curr, dist = queue.pop()
            ALL_PAIRS_CACHE[start_pos][curr] = dist
            
            for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                dx, dy = Actions.directionToVector(action)
                next_pos = (int(curr[0] + dx), int(curr[1] + dy))
                
                if next_pos not in visited and not walls[next_pos[0]][next_pos[1]]:
                    visited.add(next_pos)
                    queue.push((next_pos, dist + 1))
                    
    MAP_INITIALIZED = True

def get_distance(pos1, pos2):
    """
    - This function return the distance between two positions.
    - If the distance is not available, using Manhattan distance to calculate distance.
    """
    p1 = (int(pos1[0]), int(pos1[1]))
    p2 = (int(pos2[0]), int(pos2[1]))
    try:
        return ALL_PAIRS_CACHE[p1][p2]
    except KeyError:
        return util.manhattanDistance(p1, p2)

def scoreEvaluationFunction(currentGameState):
    return currentGameState.getScore()

def evaluation(gameState):
    """
    This function is a heuristic evaluation function to decide how good a game state is for PacMan when Alpha-Beta terminate.
    """
    if gameState.isWin():
        return 999999 + gameState.getScore()
    if gameState.isLose():
        return -999999 + gameState.getScore()

    # Consideration factors
    pacman = gameState.getPacmanPosition()
    ghosts = gameState.getGhostStates()
    foods = gameState.getFood().asList()
    capsules = gameState.getCapsules()
    score = gameState.getScore()

    # More foods or capsules remaining, larger penalty
    score -= 1.5 * len(foods)
    score -= 5.0 * len(capsules)

    # Find closest food
    # Closer food causes larger reward, therefore PacMan prefers being close to food
    if foods:
        min_food_dist = min([get_distance(pacman, food) for food in foods])  
        score += 10.0 / min_food_dist

    # Find closest capsule
    # Closer capsule causes larger reward, therefore PacMan prefers being close to capsule
    if capsules:
        min_cap_dist = min([get_distance(pacman, cap) for cap in capsules])
        score += 15.0 / min_cap_dist 

    active_ghost_dists = []
    scared_ghost_dists = []
    
    for ghost in ghosts:
        dist = get_distance(pacman, ghost.getPosition())  # Get the distance between PacMan and ghost
        if ghost.scaredTimer >= dist and dist > 0: 
            scared_ghost_dists.append(dist)
        else:
            active_ghost_dists.append(dist)

    if active_ghost_dists:  # Active ghost
        min_active_dist = min(active_ghost_dists)
        if min_active_dist <= 1:
            score -= 999999 
        elif min_active_dist < 3: 
            score -= 300.0 / min_active_dist  # Closer active ghost causes larger penalty, therefore PacMan will stay away from ghost

    if scared_ghost_dists:  # Scared ghost
        min_scared_dist = min(scared_ghost_dists)
        score += 200.0 / min_scared_dist  # Closer scared ghost causes larger reward, therefore PacMan will potentially reach the ghost

    if gameState.getPacmanState().getDirection() == Directions.STOP:  # Encorage PacMan moving
        score -= 20

    return score

class Q2_Agent(Agent):

    def __init__(self, evalFn='evaluation', depth='3'):
        self.index = 0 
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

    @log_function
    def getAction(self, gameState: GameState):
        """
        This function decides which move PacMan should make.
        """
        initialize_map_distances(gameState)  # Precomputes all-pairs shortest-path distances table
        
        logger = logging.getLogger('root')
        logger.info('AlphaBetaAgent (O(1) Perfect Maze Distance)')

        def alpha_beta_search(gameState):
            """
            This function starts Alpha-Beta search.
            """
            value, action = max_value(gameState, 0, float('-inf'), float('inf'))  # PacMan is the max player
            if action is None:
                legal_actions = gameState.getLegalActions(0)  # Get possible actions
                if legal_actions:
                    action = random.choice(legal_actions)
            return action

        def is_gameover(gameState, curr_depth):
            return curr_depth == self.depth or gameState.isWin() or gameState.isLose()

        def max_value(gameState, depth, alpha, beta):
            """
            This function represents PacMan's decision
            """
            if is_gameover(gameState, depth):  # If searching terminate, evaluate the scores
                return self.evaluationFunction(gameState), None

            v = float('-inf')
            best_action = None
            actions = gameState.getLegalActions(0)

            for action in actions:
                successor = gameState.generateSuccessor(0, action)  # Try this action
                v2, a2 = min_value(successor, depth, alpha, beta, 1)  # Turn to ghost to respond what if PacMan choose this action

                if v2 > v:
                    v, best_action = v2, action
                alpha = max(alpha, v)
                if v >= beta:  # Beta cut
                    return v, best_action

            return v, best_action

        def min_value(gameState, depth, alpha, beta, agentIndex):
            """
            This function represents ghost's decision
            """
            if is_gameover(gameState, depth):   # If searching terminate, evaluate the scores
                return self.evaluationFunction(gameState), None

            v = float('inf')
            best_action = None
            actions = gameState.getLegalActions(agentIndex)

            for action in actions:
                successor = gameState.generateSuccessor(agentIndex, action)
                
                if agentIndex == gameState.getNumAgents() - 1:
                    v2, a2 = max_value(successor, depth + 1, alpha, beta)
                else:
                    v2, a2 = min_value(successor, depth, alpha, beta, agentIndex + 1)

                if v2 < v:
                    v, best_action = v2, action
                beta = min(beta, v)
                if v <= alpha:  # Alpha cut
                    return v, best_action

            return v, best_action

        return alpha_beta_search(gameState)
        