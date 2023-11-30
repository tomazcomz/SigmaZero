import tensorflow as tf
from tensorflow import keras
from keras import layers
import numpy as np

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

# Se calhar devíamos adaptar o kernel size, devido as dimensões do tabuleiro

def convblock(input):
    c=layers.Conv2D(256,(3,3),(1,1))(input)
    b=layers.BatchNormalization()(c)
    rnl=layers.Activation(activation='softplus')(b)
    return rnl

def resblock(input):
    cb=convblock(input)
    c=layers.Conv2D(256,(3,3),(1,1))(cb)
    b=layers.BatchNormalization()(c)
    s=layers.merge([b,input],mode='sum')
    rnl=layers.Activation(activation='softplus')(s)
    return rnl

def polhead(input):
    c=layers.Conv2D(2,(1,1),(1,1))(input)
    b=layers.BatchNormalization()(c)
    rnl=layers.Activation(activation='softplus')(b)
    fc=layers.Dense()(rnl)       #output of 362
    return fc

def valhead(input):
    c=layers.Conv2D(1,(1,1),(1,1))(input)
    b=layers.BatchNormalization()(c)
    rnl=layers.Activation(activation='softplus')(b)
    # A fully connected linear layer to a hidden layer of size 256
    fcl=layers.Dense(256)(rnl)
    rnl2=layers.Activation(activation='softplus')(fcl)
    fcs=layers.Dense()(rnl2)        # flatten?!
    tanh=layers.Activation(activation='tanh')(fcs)
    return tanh

def neuraneura(l):      # l=lado
    input=layers.Input((l,l,17))
    cb=convblock(input)
    # 19 ou 39 resblocks
    ph=polhead(lastres)
    vh=valhead(lastres)