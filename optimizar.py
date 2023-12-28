from ioannina import *

def create_train_set(ds_location,game,bs=2048):
    x,y=[],[]
    for i in range(bs):
        boardfile=random.choice(os.listdir('go/datasets/boards'))
        # open file
        # if game==Go board=gen_batch()
        # labelname=boardfile em labels
        # open label
        # append
    return x,y

def train(rede: Neura,ds_location,load=True):
    x,y=create_train_set(ds_location)
    rede.compilar()
    if (load):
        rede.net.load_weights(f'pesos/{rede.name}.h5')
    for i in range(1000):
        history=rede.net.fit(x,y)
    rede.net.save_weights(f'pesos/{rede.name}.h5')