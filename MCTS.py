import math
import numpy as np

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
    def __init__(self, game_state, args, mcts,untried_actions=None, parent=None, p_action=None, prior_prob=0):
        self.game_state=game_state
        self.args=args
        self.parent=parent
        self.p_action=p_action
        self.untried_actions = self.game_state.type.check_possible_moves(self.game_state)
        self.prior_prob=prior_prob # P
        self.children=[]
        self.visit_count=0 # N
        self.total_action_value=0 # W
        self.possible=self.game_state.n**2+self.game_state.type
        self.mcts=mcts

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
        for _ in range(self.possible):
            action=self.mcts.get_act(_)
            if action in self.untried_actions:
                next_state = self.game_state.move(action[0], action[1])
                child = Node(next_state, parent=self, p_action=action, prior_prob=p[_])
                self.children.append(child)
    
    def backprop(self, v):
        self.total_action_value  += v
        self.visit_count += 1
        if self.parent is not None:
            self.parent.backprop(v)

class MCTS:
    def __init__(self, game_state, args, tind, model,eva=False):
        self.game_state=game_state
        self.args=args
        self.model=model
        self.evaluate=eva
        self.ti=tind            # ver * em ideias.md
        self.root=None # for updating root node 
        self.pi=np.zeros(self.game_state.n**2+self.game_state.type)
        self.map=self.map_act(self.root)

    def get_child(self, node, action): # find child node associated with action
        for child in node.children:
            if child.p_action==action:
                return child
        return None
    
    def map_act(self,root):
        poss=self.root.possible-self.game_state.type
        list=[self.root.possible]
        a=0
        for i in range(len(self.game_state.board)):
            for j in range(len(self.game_state.board[0])):
                list[a]=(j,i)
                a+=1
        list[a]=(-1,-1)    # adaptar para attaxx

    def get_act(self,_):
        return  self.map[_]
    
    def play(self):
        if self.root is None:
            self.root=Node(self.game_state, self.args,self)

        for _ in range(self.args['num_searches']):
            node=self.root

            # selection
            while node.fully_expanded():
                node=node.select()

            # check if node is terminal or not
            terminal=self.game_state.type.is_game_finished(node.game_state)

            # expand and evaluate
            if not terminal:
                p, v = self.model.predict(np.array([node.game_state.board]))
                p=p[0]
                v=v[0][0]
                if self.game_state.play_idx-1>self.ti or self.evaluate:
                    p=0.75*p+0.25*0.03 # adding Dirichlet noise to root's prior 
                node.expand(p) # adding children with policy from the NN to list children

            # backpropagate
            node.backprop(v)

        if self.game_state.play_idx-1<=self.ti and not self.evaluate:
            temp=1
        else:
            temp=self.args['cput']

        for child in self.root.children:
            self.pi[self.map.index(child.p_action)] = node.visit_count**(1/temp)/self.visit_count**(1/temp)

        max_prob_index = np.argmax(self.pi)
        if max_prob_index == self.game_state.n**2:
            return (-1, -1)     # definir isto como "pass"
        else:
            played=((max_prob_index // self.game_state.n), (max_prob_index % self.game_state.n))    # converter indice de array 1D em coordenadas de array 2D
            self.root=self.get_child(self.root, played) # new root node is the child corresponding to the played action
            return played