import math
import numpy as np
from go.inputconverter import *
import time
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
    def __init__(self, game_state, args, mcts, parent=None, p_action=None, prior_prob=0,play_idx=0):
        self.game_state=game_state
        self.args=args
        self.parent=parent
        self.p_action=p_action
        self.prior_prob=prior_prob   # P
        self.children=[]
        self.visit_count=0   # N
        self.total_action_value=0   # W
        self.possible=self.game_state.n**2+self.game_state.type
        self.mcts=mcts
        self.play_idx=play_idx

    def fully_expanded(self):
        return len(self.children)>0     # if no expandable moves and there are children
    
    def select(self): # chooses child with best ucb 
        if not self.fully_expanded():
            return self
        selected = max(self.children, key=lambda child: self.ucb(child))
        return selected.select()
    
    def cpuct(self, visit_count): # defining cpuct according to paper
        return math.log((visit_count+19652+1)/19652)+self.args['cpuct']
    
    def ucb(self, child): # uses variant of the PUCT algorithm
        # mean_action_value Q=W/N
        if child is None:   # to avoid 'NoneType' error
            return 0
        if child.visit_count==0:
            mean_action_value=0 
        else:
            mean_action_value=child.total_action_value/child.visit_count
        return mean_action_value+self.cpuct(self.visit_count)*child.prior_prob*(math.sqrt(self.visit_count)/(1+child.visit_count))
    

    def expand(self, p):
        for _ in range(self.possible):
            action=self.mcts.get_act(_)
            if action in self.game_state.empty_positions or action==(-1,-1):    # to avoid 'NoneType' error
                next_state = self.game_state.move(action)
                child = Node(next_state,self.args, parent=self, p_action=action, prior_prob=p[_],mcts=self.mcts,play_idx=self.play_idx+1)
                self.children.append(child)
    
    def backprop(self, v):
        self.total_action_value  += v
        self.visit_count += 1
        if self.parent is not None:
            self.parent.backprop(v)

class MCTS:
    def __init__(self, game_state, args, model,eva=False):
        self.game_state=game_state
        self.args=args
        self.model=model
        self.evaluate=eva
        self.ti=self.setind(game_state)            # ver * em ideias.md
        self.root=Node(self.game_state, self.args,self)
        self.pi=np.zeros(self.game_state.n**2+self.game_state.type)
        self.map=self.map_act()
        self.play_idx=0

    def setind(self,game):
        if game.type==0:
            match len(game.board):
                case 4:
                    tind=2
                case 6:
                    tind=3
        else:
            match len(game.board):
                case 7:
                    tind=5
                case 9:
                    tind=7
        return tind
    
    def map_act(self):
        list=[]
        for i in range(len(self.game_state.board)):
            for j in range(len(self.game_state.board[0])):
                list.append((i,j))
        list.append((-1,-1))    # adaptar para attaxx
        return list

    def get_act(self,_):
        return  self.map[_]
    
    def cut(self,action):
        for child in self.root.children:
            if child.p_action==action:
                self.root=child
                self.pi=np.zeros(self.game_state.n**2+self.game_state.type)

    def printTree(self, node, level=0, prefix=""):
        if node is not None:
            print(" " * level * 2 + f"{prefix}+- action: {node.p_action}, N: {node.visit_count}, W: {node.total_action_value}")
            for i, child in enumerate(node.children):
                self.printTree(child, level + 1, f"{prefix}|  " if i < len(node.children) - 1 else f"{prefix}   ")

    def get_play(self,passe=None):
        max_val=0
        ind=[]
        for i in range(len(self.pi)):
            if i==passe:
                continue
            val=self.pi[i]
            if val>max_val:
                ind=[i]
                max_val=self.pi[i]
                continue
            if val==max_val:
                ind.append(i)
        return random.choice(ind)
    
    def play(self):
        #print('antes ',time.time())
        for _ in range(self.args['num_searches']):
            #print('inicio ',time.time())
            node=self.root
            #print(_)
            # selection
            while node.fully_expanded():
                node=node.select()

            # check if node is terminal or not
            terminal=self.game_state.is_game_finished()
            
            # expand and evaluate
            if not terminal:
                #print('antes convert ',time.time())
                if self.game_state.type==1:
                    board=gen_batch(node.game_state)
                else:
                    board=node.game_state.board
                #print('convert ',time.time())
                p, v = self.model.net.predict(np.array([board]),batch_size=1,verbose=0)
                #print('depois ',time.time(),' ',_)
                p=p[0]
                v=v[0][0]
                p=0.75*p+0.25*np.random.dirichlet([0.2])[0] # adding Dirichlet noise to root's prior 
                node.expand(p) # adding children with policy from the NN to list children
            
            # backpropagate
            node.backprop(v)
        #print('fim ',time.time())
        
        #self.printTree(self.root)

        if self.play_idx-1<=self.ti and not self.evaluate:
            temp=1
        else:
            temp=10**(-2)

        for child in self.root.children:
            # print(child.p_action)
            if child is None:
                continue
            if child.visit_count == 0:
                self.pi[self.map.index(child.p_action)] = 0
            elif child.visit_count == 1:
                self.pi[self.map.index(child.p_action)] = 0.1
            else: 
                self.pi[self.map.index(child.p_action)] = node.visit_count**(1/temp)/child.visit_count**(1/temp)
        
        pol=self.pi
        max_prob_index=self.get_play()
        if max_prob_index == self.game_state.n**2:
            self.cut((-1,-1))
            return (-1, -1),pol     # definir isto como "pass"
        else:
            played=((max_prob_index // self.game_state.n), (max_prob_index % self.game_state.n))    # converter indice de array 1D em coordenadas de array 2D
            #self.printTree(self.root)
            print(f"Play chosen: {played}")
            self.cut(played) # new root node is the child corresponding to the played action
            return played,pol
