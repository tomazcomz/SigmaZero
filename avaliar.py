from ioannina import *
from MCTS import *
import Go
import Attaxx

ARGS = {
    'cpuct': 1.5,
    'num_searches': 100
}


def makegame(games: str): # creates gamestate
    if games=='A4x4':
        estado = Attaxx.create('4')       
    elif games=='A5x5':
        estado = Attaxx.create('5') 
    elif games=='A6x6':
        estado = Attaxx.create('6') 
    elif games=='G7x7':
        initial_board = np.zeros((7, 7),dtype=int)  
        estado = Go.GameState(initial_board)
    else:
        initial_board = np.zeros((9, 9),dtype=int)  
        estado = Go.GameState(initial_board)
    return estado


def agent_v_agent(game,alphai,alphas,sp=False):
    if game.type==0:
        return Attaxx.agent_v_agent(game,alphai,alphas,sp)
    return Go.agent_v_agent(game,alphai,alphas,sp)

def avaliar(games):
    game=makegame(games)
    icount=0
    scount=0
    for i in range(40):
        if scount>=10 and icount==0:
            break
        teta_i=Neura(game,name=get_best_name(game))
        teta_i.compilar()
        alpha_i=MCTS(game,ARGS,teta_i,True)
        teta_s=Neura(game,name='best/'+get_best_name(game))
        teta_s.compilar()
        alpha_s=MCTS(game,ARGS,teta_s,True)
        match i%2:
            case 0:
                winner=agent_v_agent(game,alpha_i,alpha_s)
                if winner==1:
                    icount+=1
                else:
                    scount+=1
            case 1:
                winner=agent_v_agent(game,alpha_s,alpha_i,)
                if winner==-1:
                    icount+=1
                else:
                    scount+=1
        print(icount)
    if icount>22:
        teta_i.make_best()
    os.remove((f'modelos/{game.name}/{str(len(game.board))}/{get_best_name(game)}.h5'))
    teta_s.copy_weights(get_best_name(game))
    return icount
