import tensorflow as tf
from tensorflow import keras
from keras import layers
import numpy as np
from keras.models import Model

""" 

input = lxlx17   -> l=lado do tabuleiro

17 feature planes:

    8 -> Xt: t={t,..,t-7}
    8 -> Yt: t={t,..,t-7}
    1 -> C: color to play

    st = [Xt, Yt, Xt−1, Yt−1,..., Xt−7, Yt−7, C].


Train:        
    ***using a mini-batch size of 8***    

"""
class Neura:
    def __init__(self,n_resblocks,game):        # loss function and learning rate?
        self.action_dim=2
        self.input(game)
        self.build(n_resblocks)
    
    def input(self,game):
        if (game.type==0):
            self.state_dim=2
            self.inpt=layers.Input((len(game.board),len(game.board[0])))
        else:
            self.state_dim=3
            self.inpt=layers.Input((len(game.board),len(game.board[0]),17))


    # Se calhar devíamos adaptar o kernel size, devido as dimensões do tabuleiro
    def convblock(self,input):
        c=layers.Conv2D(256,(3,3),(1,1))(input)
        b=layers.BatchNormalization()(c)
        rnl=layers.Activation(activation='softplus')(b)
        return rnl

    def resblock(self,input):
        cb=self.convblock(input)
        c=layers.Conv2D(256,(3,3),(1,1))(cb)
        b=layers.BatchNormalization()(c)
        s=layers.Add()([b,input])
        rnl=layers.Activation(activation='softplus')(s)
        return rnl

    def polhead(input):
        c=layers.Conv2D(2,(1,1),(1,1))(input)
        b=layers.BatchNormalization()(c)
        rnl=layers.Activation(activation='softplus')(b)
        flt=layers.Flatten()(rnl)
        fc=layers.Dense()(flt)       #output of 362 flatten?
        return fc

    def valhead(input):
        c=layers.Conv2D(1,(1,1),(1,1))(input)
        b=layers.BatchNormalization()(c)
        rnl=layers.Activation(activation='softplus')(b)
        # A fully connected linear layer to a hidden layer of size 256
        flt=layers.Flatten()(rnl)
        fcl=layers.Dense(256)(flt)
        rnl2=layers.Activation(activation='softplus')(fcl)
        fcs=layers.Dense()(rnl2)        # flatten?!
        tanh=layers.Activation(activation='tanh')(fcs)
        return tanh
    
    def loss(val,zed,pist,pol,state):
        # return sum over t (val(state(t))-z(t))^2 - pist(t) (dot) log(pol(state(t)))
        return
    
    def build(self,n_res):
        conv=self.convblock(self.inpt)
        restower=conv
        for i in range(n_res):
            restower=self.resblock(restower)
        polh=self.polhead(restower)
        valh=self.valhead(restower)
        outputs=[polh,valh]
        self.net=Model(self.inpts,outputs)
        return

    def summary(self):
        self.net.summary()
        return