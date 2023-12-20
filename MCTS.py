import math
import numpy as np
import Go
import Attaxx 
from ioannina import Neura

""" 
select, expand and evaluate, backup, play

APV-MCTS variant

N = visit_count
W = total_action_value
Q = mean_action_value
P = prior_prob of selecting that edge
exploration constant = c_puct 

Q = W/N # controlls exploitation
U = cput*p*(math.sqrt(sum_N)/(1+N)) # controlls exploration

edges (moves)
nodes (positions/states)
"""

class Node:
    def __init__(self, state, game, args, untried_actions=None, parent=None, p_action=None, prior_prob=0):
        self.game=game
        self.args=args
        self.state=state
        self.parent=parent
        self.p_action=p_action
        self.untried_actions = self.game.check_possible_moves()
        self.prior_prob=prior_prob # P
        self.children=[]
        self.visit_count=0 # N
        self.total_action_value=0 # W

    def fully_expanded(self):
        return len(self.children)>0 # if no expandable moves and there are children
    
    def select(self):
        selected=None # selected child
        max_score=-np.inf # get the max ucb obtained

        for child in self.children:
            score=self.ucb(child)
            if score>max_score:
                selected=child
                max_score=score
        
        return selected
    
    def ucb(self, child): # getting the _avantage_
        # mean_action_value Q=W/N
        if child.visit_count==0:
            mean_action_value=0 

        else:
            mean_action_value=child.total_action_value/child.visit_count

            # mean_action_value=1-((child.total_action_value/child.visit_count)+1)/2
            # '1-' as a parent we want the child that has very low mean_action_value: putting the opponent in bad pos
            # '+1' and '/2' because we want values between 0 and 1 (without it its between -1 and 1)

        return mean_action_value+self.args['cput']*child.prior_prob*(math.sqrt(self.visit_count)/(1+child.visit_count))

    def expand(self): # to do
        action = self.untried_actions.pop()
        next_state = self.game.move(action[0], action[1])
        child = Node(next_state, parent=self, p_action=action)
        return child
    
    def backprop(self, v):
        self.total_action_value  += v
        self.visit_count += 1

        if self.parent is not None:
            self.parent.backprop(v)

class MCTS:
    def __init__(self, game, args, model):
        self.game=game
        self.args=args
        self.model=model
    
    def play(self,state):
        root=Node(self.game,self.args,state)

        for search in range(self.args['num_searches']):
            node=root

            # selection
            while node.fully_expanded():
                node=node.select()

            # check if node is terminal or not
            terminal=self.game.is_game_finished()

            # expand and evaluate
            if not terminal:
                p, v = self.model.predict() # to do
                node=node.expand(p)

            # backpropagate
            node.backprop(v)

        if self.game.play_idx-1<=5:
            temp=1
        else:
            temp=0

        action_prob=np.zeros(self.game.n**2+1)
        for child in root.children:
            action_prob[child.action_taken] = node.visit_count**(1/temp)/self.visit_count**(1/temp)
        return action_prob


# test part ----------------------------------------------------------------
args = {
    'C': 10**-4,
    'num_searches': 1600
}

