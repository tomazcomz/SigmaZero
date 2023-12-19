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
    def __init__(self, state, game=Go, untried_actions=None, parent=None, p_action=None, prior_prob=0):
        self.game=game
        #self.args=args
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
        # look over each action, the probabilities given by policy
        '''
        for action, prob in enumerate(p):
            if prob>0:
                
                #child_state = self.state.copy()
                #child_state = self.game.get_next_state(child_state, action, 1)
                #child_state = self.game.change_perspective(child_state, player=-1) <- muda a persp do player
                
                child_state=self.game.create_children()
                child = Node(self.game, self.args, child_state, self, action, prob)
                self.children.append(child)'''

        action = self.untried_actions.pop()
        next_state = self.game.move(action[0], action[1])
        child = Node(next_state, parent=self, p_action=action)
        return child
    
    def backprop(self, v):
        self.total_action_value  += v
        self.visit_count += 1

        #value = self.game.get_opponent_value(value)

        if self.parent is not None:
            self.parent.backprop(v)

    def is_terminal(self):
        return self.state.is_game_finished()

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

            # value, is_terminal = self.game.get_value_and_terminated(node.state, node.action_taken)
            # value = self.game.get_opponent_value(value) <- do adversario
            """
            action taken from the parent, not the node itself, the action that was taken from the oponent on the nodes persperctive
            so if its terminal node, the player who won was the opponent, not the player of the node
            """

            # expand and evaluate
            if not terminal:
                p, v = self.model.predict() # to do
                node=node.expand(p) # expanding in all directions

            # backpropagate
            node.backprop(v)

            # talvez isto?
            if self.args['num_searches']<=30:
                temp=1
            else:
                temp=0
            choosen=node.visit_count**(1/temp)/self.visit_count**(1/temp)

        return choosen

    """ action_prob=np.zeros(self.game.action_size())
    for child in root.children:
        action_prob[child.action_taken] = child.visit_count
    action_prob/=np.sum(action_prob) # <- for turning them into probabilities
    return action_prob
    # return visit count distrbution: distribution of visit count of the children for our root node """

    def treepolicy(self):
        cur = self
        while not cur.is_terminal():
            if not cur.fully_expanded():
                return cur.expand()
            else:
                cur = cur.select()
        
        return cur


# test part ----------------------------------------------------------------
args = {
    'C': 2,
    'num_searches': 1600
}

"""
tictactoe = TicTacToe()
player = 1

args = {
    'C': 2,
    'num_searches': 1000
}

model = ResNet(tictactoe, 4, 64)
model.eval()

mcts = MCTS(tictactoe, args, model)

state = tictactoe.get_initial_state()


while True:
    print(state)
    
    if player == 1:
        valid_moves = tictactoe.get_valid_moves(state)
        print("valid_moves", [i for i in range(tictactoe.action_size) if valid_moves[i] == 1])
        action = int(input(f"{player}:"))

        if valid_moves[action] == 0:
            print("action not valid")
            continue
            
    else:
        neutral_state = tictactoe.change_perspective(state, player)
        mcts_probs = mcts.search(neutral_state)
        action = np.argmax(mcts_probs)
        
    state = tictactoe.get_next_state(state, action, player)
    
    value, is_terminal = tictactoe.get_value_and_terminated(state, action)
    
    if is_terminal:
        print(state)
        if value == 1:
            print(player, "won")
        else:
            print("draw")
        break
        
    player = tictactoe.get_opponent(player) 
"""