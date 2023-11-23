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
        self.komi = 0
    
    def is_game_finished(self):
        if self.pass_count == 2:
            return True
        
    def get_scoring(self):          # scoring: captured territories + stones + komi
        scores = {'black':0, 'white':0}
        for i in range(1,self.n-1):
            for j in range(1,self.n-1):
                if self.captured_group_size(i,j)>0:
                    pass
                    
                    
    def captured_group_size(self,i,j):        # returns 0 if this position isn't captured, otherwise returns the size of the group
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
        
def setScreen():
        width = 800
        height = 800
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Go")
        return screen
    
def drawBoard(game, screen):
    screen.fill((255,255,255)) #background branco

    #desenha frame do tabuleiro
    pygame.draw.line(screen, (0,0,0), (0,0), (800,0), 2)
    pygame.draw.line(screen, (0,0,0), (0,0), (0,800), 2)
    pygame.draw.line(screen, (0,0,0), (0,798), (800,798), 2)
    pygame.draw.line(screen, (0,0,0), (798, 0), (798,800), 2)

    #desenha linhas do tabuleiro
    for i in range(1,game.n):
        #linhas verticais
        pygame.draw.line(screen, (0,0,0), (800*i/game.n,0), (800*i/game.n,800), 2)
        #linhas horizontais
        pygame.draw.line(screen, (0,0,0), (0,800*i/game.n), (800,800*i/game.n), 2)
    
    
def main():
    n = ask_board_size()
    initial_board = np.zeros(n, n)     # initializing an empty board of size (n x n)
    captured_pieces = {'black':0, 'white':0}                      # indicates the amount of pieces captured by each player
    initial_state = GameState(initial_board,captured_pieces,0)
    pygame.init()
    screen = setScreen()
    drawBoard(initial_state, screen)
    
main()

# black plays first
# black -> 1
# white -> -1
# play ends when both players pass
# implementing positional superko rule?
# limite de jogadas: n*n*2