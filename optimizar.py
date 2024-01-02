from ioannina import *
import time
from go.inputconverter import *
import pickle

def create_train_set(game,bs=250):
    x,y=[],[]
    # x <- board
    # y <- policy, label
    for i in range(bs):
        boardfile=random.choice(os.listdir(f'{game.name}/{len(game.board)}/datasets/boards'))
        bf=pickle.load(open(f'{game.name}/{len(game.board)}/datasets/boards/{boardfile}', 'rb'))
        pf=open(f'{game.name}/{len(game.board)}/datasets/policies/{boardfile}', 'r')
        lf=open(f'{game.name}/{len(game.board)}/datasets/labels/{boardfile}', 'r')
        x.append(bf)
        y.append(pf, lf)
    return x,y


def sptrainprocd(game,policy,alphaname):
    tag=f'{alphaname}_{time.time()}'
    pfile=f'{game.name}/{len(game.board)}/datasets/policies/{tag}.txt'
    pickle.dump( gen_batch(game), open( f"{game.name}/{len(game.board)}/datasets/boards/{tag}.pkl", "wb" ) )
    np.savetxt(pfile,policy)
    return tag

def labelmaking(game,list,winner):
    for tag in list:
        file=f'{game.name}/{len(game.board)}/datasets/labels/{tag}.txt'
        with open(file, 'w') as f:
            f.write(winner)

def train(game):
    x,y=create_train_set(game)
    rede=Neura(game,name=get_best_name(game))
    rede.compilar()
    for i in range(1000):
        history=rede.net.fit(x,y)
    rede.net.save_weights(f'modelos/{rede.game.name}/{str(len(rede.game.board))}/{rede.name}.h5')
