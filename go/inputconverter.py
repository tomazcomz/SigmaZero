import numpy as np

'''
Para t<7 todos para trás, são em branco
'''

def gen_batch(gamestate):
    prev=get_previous(gamestate,7,[])
    frame=convert(gamestate,prev)
    return frame

def convert(gamestate,prev):
    frame=np.zeros(shape=(len(gamestate.board),len(gamestate.board[0]),17))
    for s in range(8):
        if s==0:
            board=gamestate.board
            #print(board)
        else:
            #print(s)
            #print(i for i in prev)
            board=prev[7-s]
            #print(board)
        for i in range(len(frame)):
            for j in range(len(frame[0])):
                if (board[i][j]==-1):
                    frame[i][j][i*2]=1
                if (board[i][j]==1):
                    frame[i][j][i*2+1]=1
                if (s==7):
                    frame[i][j][16]=gamestate.turn
    return frame

# Print disto primeiro para ver se i está correto
def get_previous(gamestate,i,list):
    #print(gamestate.parent)
    if i==0:
        list.append(gamestate.board)
        return list
    if (gamestate.parent==None):
        print(i)
        blank(gamestate,list,i)
        return np.zeros(shape=gamestate.board.shape)
    #print(gamestate.parent.board)
    i-=1
    #print(list," pre")
    get_previous(gamestate.parent,i,list)
    list.append(gamestate.board)
    #print(list," post")
    return list

def blank(gamestate,list,i):
    for j in range(i):
        list.append(np.zeros(shape=gamestate.board.shape))