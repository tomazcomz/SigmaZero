from ioannina import *
import time
from go.inputconverter import *
import pickle


# Função para criar DataSets de treino
def create_train_set(game,bs=256):
    x,yp,yv=[],[],[]
    # x <- board
    # y <- policy, label
    for i in range(bs):
        boardfile=random.choice(os.listdir(f'{game.name}/{len(game.board)}/datasets/labels'))
        bf=pickle.load(open(f'{game.name}/{len(game.board)}/datasets/boards/{boardfile[:-3]}pkl', 'rb'))
        pf=[]
        with open(f'{game.name}/{len(game.board)}/datasets/policies/{boardfile}') as f:
            for line in f:
                pf.append(float(line.strip()))
        pf=np.array(pf)
        lf=np.loadtxt(f'{game.name}/{len(game.board)}/datasets/labels/{boardfile}',ndmin=1)
        x.append(bf)
        yp.append(pf)
        yv.append(lf)
    return x,yp,yv

# Funções para guardar informação para treino
def sptrainprocd(game,policy,alphaname):
    tag=f'{alphaname}_{time.time()}'
    pfile=f'{game.name}/{len(game.board)}/datasets/policies/{tag}.txt'
    pickle.dump( gen_batch(game,True), open( f"{game.name}/{len(game.board)}/datasets/boards/{tag}.pkl", "wb" ) )
    np.savetxt(pfile,policy)
    return tag

def labelmaking(game,list,winner):
    for tag in list:
        file=f'{game.name}/{len(game.board)}/datasets/labels/{tag}.txt'
        with open(file, 'w') as f:
            f.write(str(winner))

# Função de treino: algumas alterações são necessárias para a primeira iteração
def train(game):
    #rede=Neura(game,name=get_best_name(game))
    rede=Neura(game,name='acacio')
    rede.compilar()
    for i in range(10):
        x,yp,yv=create_train_set(game)
        history=rede.net.fit(np.array(x),[np.array(yp),np.array(yv)],verbose=1,batch_size=32)
    rede.net.save_weights(f'modelos/{rede.game.name}/{str(len(rede.game.board))}/{rede.name}.h5')
