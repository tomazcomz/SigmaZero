from ioannina import *

def create_train_set(ds_location,game,bs=2048):
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
        # if game==Go board=gen_batch()
    return x,y

def train(rede: Neura,ds_location,load=True):
    x,y=create_train_set(ds_location)
    rede.compilar()
    if (load):
        rede.net.load_weights(f'pesos/{rede.name}.h5')
    for i in range(1000):
        history=rede.net.fit(x,y)
    rede.net.save_weights(f'pesos/{rede.name}.h5')