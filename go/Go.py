import pygame
import numpy as np
from utils import flood_fill


class GameState:
    def __init__(self,board,captured_pieces,play_idx,pass_count=0):
        self.n = len(board)             # number of rows and columns
        self.board = board
        self.captured_pieces = captured_pieces
        self.play_idx = play_idx        # how many overall plays occurred before this state
        self.pass_count = pass_count    # counts the current streak of 'pass' plays
    
    def is_game_finished(self):
        if self.pass_count == 2:
            return True
        
    def get_scoring(self):
        scores = {'black':0, 'white':0}
        for i in range(1,self.n-1):
            for j in range(1,self.n-1):
                if not self.has_liberties(i,j):
                    pass    #doing this
                    
    def has_liberties(self,i,j):        # returns True if the given position is part of a group with liberties and False if the group is captured
        return flood_fill(i,j,self.board)
                

        
def ask_board_size():
    inp = int(input('Board 1 - 7x7\nBoard 2 - 9x9\nChoose a board (1 or 2): '))
    if inp == 1:
        n=7
    elif inp == 2:
        n=9
    else:
        print("Invalid input. Write 1 or 2.")
        n = ask_board_size()
    return n
        
def main():
    n = ask_board_size()
    initial_board = np.zeros((n,n), dtype=int)     # initializing an empty board of size (n x n)
    captured_pieces = {'black':0, 'white':0}                      # indicates the amount of pieces captured by each player
    initial_state = GameState(initial_board,captured_pieces,0)
    
    
main()

# black plays first
# black -> 1
# white -> -1
# play ends when both players pass
# scoring: captured territories, stones and komi
# implementing positional superko rule?