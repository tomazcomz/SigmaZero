from ioannina import *
from MCTS import *
import Go
import Attaxx

ARGS = {
    'cput': 1.5,
    'num_searches': 1600
}

#def makegame(games: str):

def setind(game,size):
    tind=0
    if game.type==0:
        match size:
            case 4:
                tind=2
            case 6:
                tind=3
    else:
        match size:
            case 7:
                tind=5
            case 9:
                tind=7
    return tind

def avaliar(games,size):
    #game=makegame(games)
    icount=0
    scount=0
    for i in range(400):
        teta_i=Neura(game)
        teta_i.compilar()
        w=os.listdir(f'modelos/{games}/{size}')
        for f in w:
            iweights=f
            break
        teta_i.net.load_weights(iweights)
        alpha_i=MCTS(ARGS,tind,teta_i,True)
        teta_s=Neura(game)
        teta_s.compilar()
        w=os.listdir(f'modelos/{games}/{size}/best')
        for f in w:
            sweights=f
            break
        teta_s.net.load_weights(sweights)
        alpha_s=MCTS(ARGS,tind,teta_s,True)
        if game.type==0:
            match i%2:
                case 0:
                    winner=Attaxx.agent_v_agent(game,alpha_i,alpha_s)
                    if winner==1:
                        icount+=1
                    else:
                        scount+=1
                case 1:
                    winner=Attaxx.agent_v_agent(game,alpha_s,alpha_i)
                    if winner==2:
                        icount+=1
                    else:
                        scount+=1
        else:
            match i%2:
                case 0:
                    winner=Go.agent_v_agent(game,alpha_i,alpha_s)
                    if winner==1:
                        icount+=1
                    else:
                        scount+=1
                case 1:
                    winner=Go.agent_v_agent(game,alpha_s,alpha_i)
                    if winner==2:
                        icount+=1
                    else:
                        scount+=1
        if icount>220:
            os.remove(sweights)
            alpha_i.make_best()
            os.remove(iweights)
        else:
            os.remove(iweights)
            
