from ioannina import *
from MCTS import *
import os
from avaliar import makegame, agent_v_agent
import time
import Go,Attaxx

ARGS = {
    'cpuct': 1.5,
    'num_searches': 1600
}

def selfplay(game):
    #game=makegame(games)
    w=os.listdir(f'modelos/{game.name}/{len(game.board)}/best')
    for f in w:
        sweights=f
        break
    teta=Neura(game)
    teta.net.load_weights(sweights)
    for i in range(250000):
        alpha=MCTS(game,ARGS,teta)
        winner=agent_v_agent(game,alpha,alpha,True)
