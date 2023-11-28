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


def neuraneura(l):      # l=lado
    neura=keras.Sequential()                            # the network   
    neura.add(layers.Input(shape=(l,l,17)))
    # The input features st are processed by a residual tower that consists of a single 
    # convolutional block followed by either 19 or 39 residual blocks (4).

    # Convolutional Block:
    neura.add(layers.Conv2D(256,(3,3),(1,1)))  # perguntar Cesco sobre Conv3D
    neura.add(layers.BatchNormalization())     # ver argumentos
    neura.add(layers.softplus())