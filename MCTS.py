import math
import numpy as np
from Go import Game # é assim? file, class
from go import Go # ou assim? folder, file
# from attaxx import Attaxx 

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
    def __init__(self, game, args, state, parent=None, action=None, prior_prob=0):
        self.game=game
        self.args=args
        self.state=state
        self.parent=parent
        self.action=action
        self.prior_prob=prior_prob # P

        self.children=[]

        self.visit_count=0 # N
        self.total_action_value=0 # W

    def fully_expanded(self):
        return len(self.children)>0 # expand, if e have one child there arent anymore children we could have
    
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
            mean_action_value=1-((child.total_action_value/child.visit_count)+1)/2
            # '1-' as a parent we want the child that has very low mean_action_value: putting the opponent in bad pos
            # '+1' and '/2' because we want values between 0 and 1 (without it its between -1 and 1)

        return mean_action_value+self.args['cput']*child.prior_prob*(math.sqrt(self.visit_count)/(1+child.visit_count))

    def expand(self, p): # to do
        ...


    
    def backprop(self, v):
        self.total_action_value  += v
        self.visit_count += 1

        # parent is different player than us
        v=self.game.get_opponent_value(v) #TODOo
        if self.parent != None:
            self.parent.backprop(v)

class MCTS:
    def __init__(self, game, args, model):
        self.game=game
        self.args=args
        self.model=model
    
    def play(self,state):
        root=Node(self.game,self.args,state)

        for search in range(self.args['num_searches']):
            
            # starts from root
            node=root

            # selection
            while node.fully_expanded():
                node=node.select()

            # check if node is terminal or not
            terminal=self.game.is_game_finished()
            value=-self.game.get_winner()
            """
            action taken from the parent, not the node itself, the action that was taken from the oponent on the nodes persperctive
            so if its terminal node, the player who won was the opponent, not the player of the node
            """

            # expand and evaluate
            """
            if not terminal:
                p, v = self.model -> getting p and v from the model (e.g.: p,v=model.predict(state))
                node=node.expand(p) # expanding the node given policy
            """

            # backpropagate
            """node.backprop(v) -> given v from model"""
        
        # returning the distribution of visit counts
        action_prob=np.zeros(self.game.action_size())
        for child in root.children:
            action_prob[child.action_taken] = child.visit_count
        # turn this into probabilities
        action_prob/=np.sum(action_prob)
        return action_prob
        # return visit count distrbution: distribution of visit count of the children for our root node


# test part ----------------------------------------------------------------
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