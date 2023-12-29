import tensorflow as tf
from tensorflow import keras
from keras import layers,regularizers
import numpy as np
from keras.models import Model
import os, random
import names
from go.inputconverter import *
from shutil import copy

""" 

Train:        
    ***using a mini-batch size of 8***    

"""
class Neura:
    def __init__(self,game,n_resblocks=19,optmizador=None):        # loss function and learning rate?
        self.input(game)
        self.build(n_resblocks,self.nf)
        self.name=names.get_last_name()
        self.optmizador=optmizador

    def input(self,game):
        if (game.type==0):
            self.nf=256                 # tem que ser menos
            self.inpt=layers.Input(shape=(len(game.board),len(game.board[0]),1))
            self.passes=0
        else:
            self.nf=256
            self.passes=1
            self.inpt=layers.Input((len(game.board),len(game.board[0]),17))
        self.action_space=len(game.board)*len(game.board[0])+self.passes

    # Se calhar devíamos adaptar o kernel size, devido as dimensões do tabuleiro
    def convblock(self,input,nf):
        c=layers.Conv2D(nf,3,(1,1),'same')(input)
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
    
    def loss(pi,pol,zed,val):
        pol=np.array(pol)
        pit=np.transpose(np.array(pi))
        # return sum over t (val(state(t))-z(t))^2 - pist(t) (dot) log(pol(state(t)))
        # medium=(z-v)^2 -pi^T(dot)log(p)
        return (zed-val)**2-np.dot(pit,np.log(pol))
    
    def build(self,n_res,nf):
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
    
    def compilar(self):
        self.net.compile(optimizer=self.optmizador,loss=self.loss())

    def copy_weights(self,bestname):
        src=f'pesos/best/{bestname}.h5'
        dest=f'pesos/{self.name}.h5'
        copy(src, dest)
    
    def make_best(self):
        self.net.save_weights(f'pesos/best/{self.name}.h5')




'''------------------------------------  CUDA-RELATED  --------------------------------------------'''
def exports():   
    # Set CUDA and CUPTI paths  
    os.environ['CUDA_HOME'] = '/tomazcomz/local/cuda'
    os.environ['PATH']= '/tomazcomz/local/cuda/bin:$PATH'  
    os.environ['CPATH'] = '/tomazcomz/local/cuda/include:$CPATH'  
    os.environ['LIBRARY_PATH'] = '/tomazcomz/local/cuda/lib64:$LIBRARY_PATH'  
    os.environ['LD_LIBRARY_PATH'] = '/tomazcomz/local/cuda/extras/CUPTI/lib64:$LD_LIBRARY_PATH'  
    os.environ['LD_LIBRARY_PATH'] = '/tomazcomz/local/cuda/lib64:$LD_LIBRARY_PATH'

def opts():
    os.environ['CUDA_CACHE_DISABLE'] = '0'                  # disable caching
    os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'        # starts on memory subset then grows
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'                # info and wawrning supressed
    os.environ['TF_GPU_THREAD_MODE'] = 'gpu_private'        # gpu kernels running in parallel threads
    #os.environ['TF_USE_CUDNN_BATCHNORM_SPATIAL_PERSISTENT'] = '1'      check spatial persistent bnormalization
    os.environ['TF_ENABLE_WINOGRAD_NONFUSED'] = '1'         # check for more info