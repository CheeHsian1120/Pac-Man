# qlearningAgents.py
# ------------------
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


from game import *
from agents.learningAgents import ReinforcementAgent
from pacman import GameState

import random,util,math
import numpy as np
from game import Directions
import json


class Q2Agent(ReinforcementAgent):
    """
      Q-Learning Agent

      Methods you should fill in:
        - __init__
        - registerInitialState
        - update
        - getParams
        - epsilonGreedyActionSelection

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)
    """

    def __init__(self, usePresetParams=False, **args):
        """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
            python pacman.py -p Q2Agent -a epsilon=0.1

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes

        usePresetParams - Set to True if you want to use your evaluation parameters
        """

        self.index = 0  # This is always Pacman

        ReinforcementAgent.__init__(self, **args)

        # when maze size is provided use the preset parameters, otherwise values will use those specified at the command line
        if usePresetParams:
            self.epsilon = self.getParams("epsilon")
            self.alpha = self.getParams("alpha")
            self.discount = self.getParams("gamma")

        # *** YOUR CODE STARTS HERE ***

        self.Qtable = util.Counter()

        # *** YOUR CODE ENDS HERE ***
    

    def registerInitialState(self, state: GameState):
        """
        Don't modify this method except in the provided area.
        You can modify this method to do any computation you need at the start of each episode
        """

        # *** YOUR CODE STARTS HERE ***

        

        # *** YOUR CODE ENDS HERE ***

        self.startEpisode()
        if self.episodesSoFar == 0:
            print('Beginning %d episodes of Training' % (self.numTraining))
    
    
    def getAction(self, state: GameState):
        """
        Don't modify this method!
        Uses epsilon greedy to select an action based on the agents Q table.
        """

        action = self.epsilonGreedyActionSelection(state)
        self.doAction(state, action)
        return action

    def update(self, state: GameState, action: str, nextState: GameState, reward):
        """
        The parent class calls this to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here using the Q value update equation

        NOTE: You should never call this function,
        it will be called on your behalf
        """

        # *** YOUR CODE HERE ***
        cust_state = self.getCustomState(state)
        cust_next_state = self.getCustomState(nextState)
        next_actions = self.getPossibleActions(nextState)

        if not next_actions:
            max_next_q_value = 0.0
        else:
            max_next_q_value = float("-inf")

            for next_action in next_actions:
                next_q_value = self.Qtable[(cust_next_state, next_action)]

                if next_q_value > max_next_q_value:
                    max_next_q_value = next_q_value

        q_value = self.Qtable[(cust_state, action)]
        new_q_value = q_value + self.alpha * (reward + self.discount * max_next_q_value - q_value)
        self.Qtable[(cust_state, action)] = new_q_value

    def getParams(self, param_name):
        """
        Add your parameters here 
        """
        params = {
            "gamma": 0.99,
            "epsilon": 0.1,
            "alpha": 0.30
        }
        return params[param_name]


    def epsilonGreedyActionSelection(self, state: GameState):
        """
        Compute the action to take in the current state.  With
        probability self.epsilon, we should take a random action and
        take the best policy action otherwise.  Note that if there are
        no legal actions, which is the case at the terminal state, you
        should choose None as the action.

        HINT: When the agent is no longer in training self.epsilon will be set to 0, 
        so calling this method should always return the best action over the Q values
        HINT: You might want to use util.flipCoin(prob)
        HINT: To pick randomly from a list, use random.choice(list)
        HINT: You might want to use self.getLegalActions(state), 
        but consider whether or not using the STOP action is necessary or beneficial
        """
        
        # *** YOUR CODE HERE ***
        actions = self.getPossibleActions(state)  # Get all possible actions

        if not actions:  # Do not have any action
            return None

        # During testing phase, remove STOP if Pacman is very close to ghost (distance <= 1)
        # Training phase will not be affected
        if self.isInTesting() and Directions.STOP in actions and len(actions) > 1:
            pacman_pos = state.getPacmanPosition()
            ghost_pos = state.getGhostPosition(1)
            distance = util.manhattanDistance(pacman_pos, ghost_pos)

            if distance <= 1:
                actions.remove(Directions.STOP)

        cust_state = self.getCustomState(state)  # Retrieve customized state

        if util.flipCoin(self.epsilon):  # Epsilon-Greedy (Exploitation & Exploration)
            return random.choice(actions)

        # Find the best Q-value at the current action
        best_value = float("-inf")
        best_actions = []
        
        for action in actions:
            q_value = self.Qtable[(cust_state, action)]

            if q_value > best_value:  # Find the best action
                best_value = q_value
                best_actions = [action]
            elif q_value == best_value:  # Tie breaking
                best_actions.append(action)

        return random.choice(best_actions)

    ################################ ANY OTHER CODE BELOW HERE ################################

    def getCustomState(self, state: GameState):
        """
        This function extracts neccassary state for Q-Learning.
        """
        pacman_pos = state.getPacmanPosition()
        ghost_pos = state.getGhostPosition(1)
        food_grid = tuple(sorted(state.getFood().asList()))
        return (pacman_pos, ghost_pos, food_grid)


    def getPossibleActions(self, state: GameState):
        """
        This function returns all legal actions.
        If the distance between Pacman and ghost is less than 2, recover all actions (include STOP).
        """
        actions = state.getLegalPacmanActions()

        if Directions.STOP in actions:
            actions.remove(Directions.STOP)

        if not actions:
            return []

        pacman_pos = state.getPacmanPosition()
        ghost_pos = state.getGhostPosition(1)
        distance = util.manhattanDistance(pacman_pos, ghost_pos)

        if distance <= 2:
            actions = state.getLegalPacmanActions()

        return actions