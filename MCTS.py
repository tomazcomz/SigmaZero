import math
import numpy as np
import Go
""" import OldGo
import Attaxx 
from ioannina import Neura
 """

""" 
select, expand and evaluate, backup, play

APV-MCTS variant

N = visit_count
W = total_action_value
Q = mean_action_value
P = prior_prob of selecting that edge
exploration constant = cpuct 

Q = W/N # controlls exploitation
U = cput*p*(math.sqrt(sum_N)/(1+N)) # controlls exploration

edges (moves)
nodes (positions/states)
"""

class Node:
    def __init__(self, game_state, args, untried_actions=None, parent=None, p_action=None, prior_prob=0):
        self.game_state=game_state
        self.args=args
        self.parent=parent
        self.p_action=p_action
        self.untried_actions = Go.check_possible_moves(self.game_state)
        self.prior_prob=prior_prob # P
        self.children=[]
        self.visit_count=0 # N
        self.total_action_value=0 # W

    def fully_expanded(self):
        return len(self.children)>0 # if no expandable moves and there are children
    
    def select(self): # chooses child with best ucb 
        if not self.children:
            return None
        selected = max(self.children, key=lambda child: self.ucb(child))
        return selected.select()
    
    def cpuct(self, visit_count): # defining cpuct according to paper
        return math.log((visit_count+19652+1)/19652)+self.args['cpuct']
    
    def ucb(self, child): # uses variant of the PUCT algorithm
        # mean_action_value Q=W/N
        if child.visit_count==0:
            mean_action_value=0 
        else:
            mean_action_value=child.total_action_value/child.visit_count
        return mean_action_value+self.cpuct(self.visit_count)*child.prior_prob*(math.sqrt(self.visit_count)/(1+child.visit_count))

    def expand(self, p):
        for _ in range(self.untried_actions.len()):
            action = self.untried_actions.pop() # coordenada
            next_state = self.game_state.move(action[0], action[1])
            child = Node(next_state, parent=self, p_action=action, prior_prob=p)
            self.children.append(child)
    
    def backprop(self, v):
        self.total_action_value  += v
        self.visit_count += 1
        if self.parent is not None:
            self.parent.backprop(v)

class MCTS:
    def __init__(self, args,tind, model,eva=False):
        self.args=args
        self.model=model
        self.evaluate=eva
        self.ti=tind            # ver * em ideias.md
        self.root=None # for updating root node 
        self.pi=np.zeros(self.game_state.n**2+1)

    def get_child(self, node, action): # find child node associated with action
        for child in node.children:
            if child.p_action==action:
                return child
        return None
    
    def play(self):
        if self.root is None:
            self.root=Node(self.game_state, self.args)

        for _ in range(self.args['num_searches']):
            node=self.root

            # selection
            while node.fully_expanded():
                node=node.select()

            # check if node is terminal or not
            terminal=Go.is_game_finished(node.game_state)

            # expand and evaluate
            if not terminal:
                p, v = self.model.predict(np.array([node.game_state.board]))
                if self.game_state.play_idx-1>self.ti or self.evaluate:
                    p=0.75*p+0.25*0.03 # adding Dirichlet noise to root's prior 
                node.expand(p) # adding childs with policy from the NN to list children

            # backpropagate
            node.backprop(v)

        if self.game_state.play_idx-1<=self.ti and not self.evaluate:
            temp=1
        else:
            temp=self.args['cput']

        """ action_prob=np.zeros(self.game_state.n**2+1)
        for child in self.root.children:
            action_prob[child.action_taken] = node.visit_count**(1/temp)/self.visit_count**(1/temp) """
        
        for child in self.root.children:
            self.pi[child.action_taken] = node.visit_count**(1/temp)/self.visit_count**(1/temp)

        #max_prob_index = np.argmax(action_prob)
        max_prob_index = np.argmax(self.pi)
        if max_prob_index == self.game_state.n**2:
            return (-1, -1)     # definir isto como "pass"
        else:
            played=((max_prob_index // self.game_state.n), (max_prob_index % self.game_state.n))    # converter indice de array 1D em coordenadas de array 2D
            self.root=self.get_child(self.root, played) # new root node is the child corresponding to the played action
            return played
    

