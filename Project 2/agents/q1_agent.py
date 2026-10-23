# PacmanValueIterationAgent.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

#---------------------#
# DO NOT MODIFY BEGIN #
#---------------------#
import util

from agents.learningAgents import ValueEstimationAgent
from game import Grid, Actions, Directions
import math
from pacman import GameState
import random
import numpy as np
import json


class Q1Agent(ValueEstimationAgent):
    """
    Q1 agent takes a Markov decision process
    (see pacmanMDP.py) on initialization and 
    runs value iteration or policy iteration
    for a given number of iterations using the supplied
    discount factor.
    """

    def __init__(self, mdp="PacmanMDP", discount=0.5, iterations=200, mazeSize=None):
        """
          Your agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will likely use:
              self.MDP.getStates()
              self.MDP.getPossibleActions(state)
              self.MDP.getTransitionStatesAndProbs(state, action)
              self.MDP.getReward(state, action)
              self.MDP.isTerminal(state)
        """
        mdp_func = util.import_by_name('./', mdp)
        self.mdp_func = mdp_func

        print('[Q1Agent] using mdp ' + mdp_func.__name__)
        
        # set discount factor and the number of training iterations
        if mazeSize:
            self.discount = self.getParams(mazeSize, "gamma")
            self.iterations = self.getParams(mazeSize, "iterations")
        else:
            self.discount = float(discount)
            self.iterations = int(iterations)            

        # initialise the values and policy. You will update them in solveMDP
        self.values = None
        self.policy = None

        # flag so we only solve the MDP once no matter how many games we play
        self.mdp_solved = False


    def getAction(self, gameState: GameState):
        """
        Returns the action to take at the a location according to the values

        Note: reaching any positive terminal state is considered winning the game and results in +500 points
        To achieve this we need the ReachedPositiveTerminalStateException because the game wouldn't noramlly end with food remaining
        """

        pacman_location = gameState.getPacmanPosition()
        if pacman_location in self.MDP.getFoodStates():
            raise util.ReachedPositiveTerminalStateException("Reached a Positive Terminal State")
        else:
            best_action = self.deriveActionFromLearntPolicy(pacman_location)
            return self.MDP.applyNoiseToAction(pacman_location, best_action)

    def registerInitialState(self, gameState: GameState):

        # set up the mdp with the agent starting state and solve it
        self.MDP = self.mdp_func(gameState)

        # only attempt to solve the MDP once
        if not self.mdp_solved:
            self.mdp_solved = True
            self.solveMDP()

    #-------------------#
    # DO NOT MODIFY END #
    #-------------------#

    def getParams(self, maze_size, param_name):
        """
        Add your maze parameters here 
        """
        params = {
            "small": {
                "gamma": 0.99,
                "iterations": 100
                },
            "medium": {
                "gamma": 0.995,
                "iterations": 100
            },
            "large": {
                "gamma": 0.5,
                "iterations": 100
            }
        }
        return params[maze_size][param_name]
    

    def solveMDP(self):
        """
        This function will solve the mdp instance the agent received on input.
        This is where you implement either policy iteration or value iteration
        You can access the 
        - mdp with self.mdp
        - discount factor with self.discount
        - num of iteratons with self.iterations
        """
        # "*** YOUR CODE HERE ***"
        self.values = util.Counter()  # V values from the previous iteration
        self.policy = {}  # Store the best action for each state

        # Number of iterations
        for _ in range(self.iterations):
            new_values = util.Counter()  # V values for this iteration

            # A set of all reachable states
            for state in self.MDP.getStates():
                if self.MDP.isTerminal(state):
                    new_values[state] = 0
                    continue

                best_value = float("-inf")  # Use to record the larger expected utility of all possible actions for the current state

                # A set of all possible actions
                for action in self.MDP.getPossibleActions(state):
                    expected_util = self.getQValue(state, action, self.values)

                    # Find the best action
                    if expected_util > best_value:
                        best_value = expected_util

                new_values[state] = best_value
            self.values = new_values

        # Get the policy from the final V values
        for state in self.MDP.getStates():
            if self.MDP.isTerminal(state):
                self.policy[state] = None
                continue

            best_value = float("-inf")
            best_action = None

            for action in self.MDP.getPossibleActions(state):
                expected_util = self.getQValue(state, action, self.values)

                if expected_util > best_value:
                    best_value = expected_util
                    best_action = action

            self.policy[state] = best_action

    
    def deriveActionFromLearntPolicy(self, state: tuple):
        """
        This functions takes an (x,y) tuple representing Pac-Man's location
        and decides how to act using the agent's learnt policy.

        If you used Value Iteration this will be derived from the values you compute
        If you use Policy Iteration this will come directly from the computed policy
        """
        # "*** YOUR CODE HERE ***"
        if self.MDP.isTerminal(state):
            return None

        return self.policy[state]


    ################################ ANY OTHER CODE BELOW HERE ################################

    def getQValue(self, state, action, values):
        expected_util = 0

        # Retrieve all possible next actions with corresponding probability
        for next_state, prob in self.MDP.getTransitionStatesAndProbs(state, action):
            reward = self.MDP.getReward(state, action, next_state)  # Reward of the current step
            expected_util += prob * (reward + self.discount * values[next_state])  # Q-value

        return expected_util