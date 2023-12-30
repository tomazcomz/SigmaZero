from ioannina import *
import time

def create_train_set(game,bs=2048):
    x,y=[],[]
    # x <- board
    # y <- policy, label
    for i in range(bs):
        boardfile=random.choice(os.listdir(f'{game.name}/{len(game.board)}/datasets/boards'))
        bf=open(f'{game.name}/{len(game.board)}/datasets/boards/{boardfile}', 'r')
        pf=open(f'{game.name}/{len(game.board)}/datasets/policies/{boardfile}', 'r')
        lf=open(f'{game.name}/{len(game.board)}/datasets/labels/{boardfile}', 'r')
        x.append(bf)
        y.append(pf, lf)
    return x,y


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

def train(rede: Neura,game,load=True):
    x,y=create_train_set(game)
    rede.compilar()
    if (load):
        rede.net.load_weights(f'pesos/{rede.name}.h5')
    for i in range(1000):
        history=rede.net.fit(x,y)
    rede.net.save_weights(f'pesos/{rede.name}.h5')