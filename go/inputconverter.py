import numpy as np

def gen_batch(gamestate):
    prev=get_previous(gamestate,8,[])
    frame=convert(gamestate,prev)
    return frame

def convert(gamestate,prev):
    frame=np.zeros(shape=(len(gamestate.board),len(gamestate.board[0]),17))
    for s in range(8):
        if s==0:
            board=gamestate.board
        else:
            board=prev[7-s]
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
    i-=1
    if i==0:
        list.append(gamestate.board)
        return list
    list.append(get_previous(gamestate.previous_states[0]),i,list)
    return list