from ioannina import *
from MCTS import *
import Go
import Attaxx

ARGS = {
    'cput': 1.5,
    'num_searches': 1000
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

def avaliar(games,size):
    game=makegame(games)
    icount=0
    scount=0
    for i in range(400):
        w=os.listdir(f'modelos/{games}/{size}')
        for f in w:
            iweights=f[:-3]
            break
        teta_i=Neura(game,name=iweights,n_resblocks=len(game.board))
        teta_i.compilar()
        alpha_i=MCTS(ARGS,teta_i,True)
        teta_s=Neura(game,name=get_best_name(game),n_resblocks=len(game.board))
        teta_s.compilar()
        alpha_s=MCTS(ARGS,teta_s,True)
        match i%2:
            case 0:
                winner=agent_v_agent(game,alpha_i,alpha_s)
            case 1:
                winner=agent_v_agent(game,alpha_s,alpha_i,)
        if winner==1:
            icount+=1
        else:
            scount+=1
    if icount>220:
        alpha_i.make_best()
    os.remove((f'modelos/{game.name}/{str(len(game.board))}/best/{iweights}.h5'))
            
