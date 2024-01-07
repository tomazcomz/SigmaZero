from ioannina import *
from MCTS import *
import os
from avaliar import makegame, agent_v_agent
import time
import Go,Attaxx

ARGS = {
    'cpuct': 1.5,
    'num_searches': 100
}


def rmfiles(game):
    for i in range(250):
        w=os.listdir(f'{game.name}/{len(game.board)}/datasets/labels')
        for f in w:
            boardfile=f
            break
        os.remove(f'{game.name}/{len(game.board)}/datasets/boards/{boardfile}')
        os.remove(f'{game.name}/{len(game.board)}/datasets/policies/{boardfile}')
        os.remove(f'{game.name}/{len(game.board)}/datasets/labels/{boardfile}')

def sp(game):
    #teta=Neura(game,name=get_best_name(game))   
    for i in range(50):
        teta=Neura(game,name='acacio')   # comentar isto
        alpha=MCTS(game,ARGS,teta)
        winner=agent_v_agent(game,alpha,alpha,True)
