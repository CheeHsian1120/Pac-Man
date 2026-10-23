import logging
import time
from typing import Tuple

import util
from game import Actions, Agent, Directions
from logs.search_logger import log_function
from pacman import GameState


class q1b_problem:
    """
    This search problem finds paths through all four corners of a layout.

    You must select a suitable state space and successor function
    """
    def __str__(self):
        return str(self.__class__.__module__)

    def __init__(self, gameState: GameState):
        """
        Stores the start and goal.

        gameState: A GameState object (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.startingGameState: GameState = gameState
        self.directions = [
            Directions.NORTH,
            Directions.SOUTH,
            Directions.EAST,
            Directions.WEST
        ]

    @log_function
    def getStartState(self):
        "*** YOUR CODE HERE ***"
        init_loc = self.startingGameState.getPacmanPosition()  # Retrieve Pac Man initial position
        # A set data structure cannot store any unhashable (mutable) object, so we use frozenset
        food_list = frozenset(self.startingGameState.getFood().asList())  # Retrieve all foods' position on the maze
        return (init_loc, food_list)  # Pack them as a tuple

    @log_function
    def isGoalState(self, state):
        "*** YOUR CODE HERE ***"
        return len(state[1]) == 0  # Unpack the tuple and check if food list is empty

    @log_function
    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """
        "*** YOUR CODE HERE ***"
        successors = []
        step_cost = 1
        curr_loc, curr_foods = state

        for action in self.directions:
            next_loc = Actions.getSuccessor(curr_loc, action)  # Get the next state to decide where to go
            new_x, new_y = int(next_loc[0]), int(next_loc[1])
            next_loc = (new_x, new_y)

            if not self.startingGameState.hasWall(new_x, new_y):
                next_foods = curr_foods  # Next state do not contain food, keep original food list
                if next_loc in curr_foods:
                    next_foods = curr_foods - frozenset([next_loc])  # Remove that consumed food position

                next_state = (next_loc, next_foods)
                successors.append((next_state, action, step_cost))

        return successors
