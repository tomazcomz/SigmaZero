import tensorflow as tf
from tensorflow import keras
from keras import layers,regularizers,optimizers
import numpy as np
from keras.models import Model
import os, random
import names
from go.inputconverter import *
from shutil import copy
import math

""" 

Train:        
    ***using a mini-batch size of 8***    

"""
class Neura:
    def __init__(self,game,name=None):        # loss function and learning rate?
        self.input(game)
        self.game=game
        #self.res=len(game.board)
        self.res=19
        self.build(self.res,self.nf)
        if name=='acacio':
            self.name='acacio'+game.name+str(len(game.board))+str(self.res)
        elif name==None:
            self.name=names.get_last_name()+game.name+str(len(game.board))+str(self.res)
            self.net.save_weights(f'modelos/{game.name}/{str(len(game.board))}/{self.name}.h5')
        else:
            self.name=name
            self.net.load_weights(f'modelos/{game.name}/{str(len(game.board))}/{self.name}.h5')
        

    def input(self,game):
        if (game.type==0):
            self.nf=math.ceil(len(game.board)**2*0.709+len(game.board)**2)                 
            self.inpt=layers.Input(shape=(len(game.board),len(game.board[0]),1))
            self.passes=0
        else:
            self.nf=math.ceil(len(game.board)**2*0.709+len(game.board)**2)
            #self.nf=256
            self.passes=1
            self.inpt=layers.Input((len(game.board),len(game.board[0]),17))
        self.action_space=len(game.board)*len(game.board[0])+self.passes
       #self.res=len(game.board)

    # Se calhar devíamos adaptar o kernel size, devido as dimensões do tabuleiro
    def convblock(self,input,nf):
        c=layers.Conv2D(nf,3,(1,1),'same')(input)
        b=layers.BatchNormalization()(c)
        rnl=layers.Activation(activation='softplus')(b)
        return rnl
    
    def convblock3(self,input,nf):
        c=layers.Conv3D(nf,3,(1,1,1),'same')(input)
        b=layers.BatchNormalization()(c)
        rnl=layers.Activation(activation='softplus')(b)
        return rnl

    def resblock(self,input,i,nf):
        cb=self.convblock(input,nf)
        c=layers.Conv2D(nf,3,(1,1),'same')(cb)
        b=layers.BatchNormalization()(c)
        s=layers.Add()([b,input])
        rnl=layers.Activation(activation='softplus',name=f'endrestower{i}')(s)
        return rnl
    
    def resblock3(self,input,i,nf):
        cb=self.convblock3(input,nf)
        c=layers.Conv3D(nf,3,(1,1,1),'same')(cb)
        b=layers.BatchNormalization()(c)
        s=layers.Add()([b,input])
        rnl=layers.Activation(activation='softplus',name=f'endrestower{i}')(s)
        return rnl

    def polhead(self,input):
        c=layers.Conv2D(2,1,(1,1),'same',name='convpol')(input)
        b=layers.BatchNormalization(name='bnpol')(c)
        rnl=layers.Activation(activation='softplus',name='rnlpol')(b)
        flt=layers.Flatten(name='polflat')(rnl)
        fc=layers.Dense(units=self.action_space,name='polout',kernel_regularizer=regularizers.L2(0.0001))(flt)  
        return fc

    def valhead(self,input,nf):
        c=layers.Conv2D(1,1,(1,1),'same')(input)
        b=layers.BatchNormalization()(c)
        rnl=layers.Activation(activation='softplus')(b)
        flt=layers.Flatten()(rnl)
        fcl=layers.Dense(nf,kernel_regularizer=regularizers.L2(0.0001))(flt)
        rnl2=layers.Activation(activation='softplus')(fcl)
        fcs=layers.Dense(1,kernel_regularizer=regularizers.L2(0.0001))(rnl2)
        tanh=layers.Activation(activation='tanh',name='valout')(fcs)
        return tanh    
    
    def build(self,n_res,nf,):
        conv=self.convblock(self.inpt,nf)
        restower=conv
        for i in range(n_res):
            restower=self.resblock(restower,i,nf)
        polh=self.polhead(restower)
        valh=self.valhead(restower,nf)
        outputs=[polh,valh]
        self.net=Model(self.inpt,outputs)
        return

    def summary(self):
        self.net.summary()
        return
    
    def compilar(self,lr=0.01):
        self.net.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=lr,momentum=0.9),loss={'polout':tf.keras.losses.CategoricalCrossentropy(),'valout':tf.keras.losses.MeanSquaredError()})

    def copy_weights(self,bestname):
        src=f'modelos/{self.game.name}/{str(len(self.game.board))}/best/{bestname}.h5'
        dest=f'modelos/{self.game.name}/{str(len(self.game.board))}/{self.name}.h5'
        copy(src, dest)
    
    def make_best(self):
        os.remove((f'modelos/{self.game.name}/{str(len(self.game.board))}/best/{self.get_best_name()}.h5'))
        self.net.save_weights(f'modelos/{self.game.name}/{str(len(self.game.board))}/best/{self.name}.h5')

    def get_best_name(self):
        folder_path = f"modelos/{self.game.name}/{len(self.game.board)}/best"
        entries = os.listdir(folder_path)
        for e in entries:
            file_name = e
            break
        return file_name[:-3]

def get_best_name(game):
    folder_path = f"modelos/{game.name}/{len(game.board)}/best"
    entries = os.listdir(folder_path)
    file_name = None
    for e in entries:
        file_name = e
        break
    return file_name[:-3]

def sigmaloss(y_true,y_pred):
        pol=y_pred[0]
        pit=np.transpose(np.array(y_true[0]))
        # return sum over t (val(state(t))-z(t))^2 - pist(t) (dot) log(pol(state(t)))
        # medium=(z-v)^2 -pi^T(dot)log(p)
        return (y_pred[1]-y_true[1])**2-np.dot(pit,np.log(pol))


'''------------------------------------  CUDA-RELATED  --------------------------------------------'''
def exports():   
    # Set CUDA and CUPTI paths  
    os.environ['CUDA_HOME'] = '/usr/local/cuda'
    os.environ['PATH']= '/usr/local/cuda/bin:$PATH'  
    os.environ['CPATH'] = '/usr/local/cuda/include:$CPATH'  
    os.environ['LIBRARY_PATH'] = '/usr/local/cuda/lib64:$LIBRARY_PATH'  
    os.environ['LD_LIBRARY_PATH'] = '/usr/local/cuda/extras/CUPTI/lib64:$LD_LIBRARY_PATH'  
    os.environ['LD_LIBRARY_PATH'] = '/usr/local/cuda/lib64:$LD_LIBRARY_PATH'

def opts():
    os.environ['CUDA_CACHE_DISABLE'] = '0'                  # disable caching
    os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'        # starts on memory subset then grows
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'                # info and wawrning supressed
    os.environ['TF_GPU_THREAD_MODE'] = 'gpu_private'        # gpu kernels running in parallel threads
    #os.environ['TF_USE_CUDNN_BATCHNORM_SPATIAL_PERSISTENT'] = '1'      check spatial persistent bnormalization
    os.environ['TF_ENABLE_WINOGRAD_NONFUSED'] = '1'         # check for more info