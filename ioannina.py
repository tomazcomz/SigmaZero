import tensorflow as tf
from tensorflow import keras
from keras import layers
import numpy as np
from keras.models import Model

""" 

Train:        
    ***using a mini-batch size of 8***    

"""
class Neura:
    def __init__(self,n_resblocks,game):        # loss function and learning rate?
        self.input(game)
        self.build(n_resblocks,self.nf)
    
    def input(self,game):
        if (game.type==0):
            self.state_dim=2
            self.nf=256                 # tem que ser menos
            self.inpt=layers.Input(shape=(len(game.board),len(game.board[0]),1))
        else:
            self.state_dim=3
            self.nf=256 
            self.inpt=layers.Input((len(game.board),len(game.board[0]),17))


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
        fc=layers.Dense(units=37,name='')(flt)       #output of 362 flatten?
        return fc

    def valhead(self,input,nf):
        c=layers.Conv2D(1,1,(1,1),'same')(input)
        b=layers.BatchNormalization()(c)
        rnl=layers.Activation(activation='softplus')(b)
        flt=layers.Flatten()(rnl)
        fcl=layers.Dense(nf)(flt)
        rnl2=layers.Activation(activation='softplus')(fcl)
        fcs=layers.Dense(1)(rnl2)
        tanh=layers.Activation(activation='tanh',name='valout')(fcs)
        return tanh
    
    def loss(val,zed,pist,pol,state):
        # return sum over t (val(state(t))-z(t))^2 - pist(t) (dot) log(pol(state(t)))
        return
    
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