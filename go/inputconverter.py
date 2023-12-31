import numpy as np
import random
'''
Para t<7 todos para trás, são em branco
'''

def gen_batch(gamestate, tr=False):
    ti=random.choice(range(8))
    prev=get_previous(gamestate,8,[],ti,tr)
    #print(len(prev))
    frame=convert(gamestate,prev)
    return frame

def convert(gamestate,prev):
    frame=np.zeros(shape=(len(gamestate.board),len(gamestate.board[0]),17))
    for s in range(8):
        board=prev[7-s]
        for i in range(len(frame)):
            for j in range(len(frame[0])):
                if (board[i][j]==gamestate.turn):
                    frame[i][j][s*2]=1
                if (board[i][j]==-gamestate.turn):
                    frame[i][j][s*2+1]=1
                if (s==7):
                    #print(board)
                    frame[i][j][16]=gamestate.turn
    return frame

def get_previous(gamestate,i,list,ti,tr):
    if i==1:
        list.append(transform(gamestate.board, ti,tr))
        return list
    if (gamestate.parent==None):
        blank(gamestate,list,i)
        return list
    i-=1
    get_previous(gamestate.parent,i,list,ti,tr)
    list.append(transform(gamestate.board, ti,tr))
    return list

def transform(board, ti,tr):
    if tr:
        if ti>3:
            board = np.flipud(board)
            ti -= 4
        return np.rot90(board, ti)
    return board


def blank(gamestate,list,i):
    for j in range(i):
        list.append(np.zeros(shape=gamestate.board.shape))