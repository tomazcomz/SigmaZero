from ioannina import *
from MCTS import *
import os
from avaliar import makegame, setind
import time
from Go import agent_v_agent

ARGS = {
    'cput': 10**-4,
    'num_searches': 1600
}

def sptrainprocd(board,alphaname):
    tag=f'{alphaname}_{time.time()}'
    file=f'datasets/boards/{tag}.txt'
    np.savetxt(file,board)
    return tag

def labelmaking(list,winner):
    for tag in list:
        file=f'datasets/labels/{tag}.txt'
        with open(file, 'w') as f:
            f.write(winner)

def selfplay(games,size):
    game=makegame(games)
    tind=setind(game,size)
    w=os.listdir(f'modelos/{games}/{size}/best')
    for f in w:
        sweights=f
        break
    teta=Neura(game)
    teta.net.load_weights(sweights)
    for i in range(250000):
        alpha=MCTS(ARGS,tind,teta)
        agent_v_agent(game,alpha,alpha,True)
        