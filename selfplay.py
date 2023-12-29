from ioannina import *
from MCTS import *
import os
from avaliar import makegame, setind
import time
from Go import agent_v_agent

ARGS = {
    'cpuct': 1.5,
    'num_searches': 1600
}

def sptrainprocd(game,policy,alphaname):
    tag=f'{alphaname}_{time.time()}'
    pfile=f'{game.name}/{len(game.board)}/datasets/policies/{tag}.txt'
    file=f'{game.name}/{len(game.board)}/datasets/boards/{tag}.txt'
    np.savetxt(file,game.board)
    np.savetxt(pfile,policy)
    return tag

def labelmaking(game,list,winner):
    for tag in list:
        file=f'{game.name}/{len(game.board)}/datasets/labels/{tag}.txt'
        with open(file, 'w') as f:
            f.write(winner)

def selfplay(games):
    game=makegame(games)
    tind=setind(game,len(game.board))
    w=os.listdir(f'modelos/{games}/{len(game.board)}/best')
    for f in w:
        sweights=f
        break
    teta=Neura(game)
    teta.net.load_weights(sweights)
    for i in range(250000):
        alpha=MCTS(ARGS,tind,teta)
        agent_v_agent(game,alpha,alpha,True)
        