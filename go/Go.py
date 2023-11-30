import pygame
import numpy as np
import copy as cp
from utils import flood_fill


class GameState:
    def __init__(self,board,turn,captured_pieces,play_idx,pass_count=0):
        self.n = len(board)             # number of rows and columns
        self.board = board
        self.captured_pieces = captured_pieces
        self.turn = turn                # who's playing next
        self.play_idx = play_idx        # how many overall plays occurred before this state
        self.pass_count = pass_count    # counts the current streak of 'pass' plays
        self.komi = 0
        self.end = -1
    
    def is_game_finished(self):
        if self.pass_count == 2:
            return True
        
    def get_scores(self):          # scoring: captured territories + player's stones + komi
        visited = [[False for i in range(self.n)] for j in range(self.n)]
        scores = {1:0, -1:0}
        
        scores[-1] += self.komi
        
                    
    # returns None if this position isn't captured, otherwise it returns the positions of the captured group to which (i,j) belongs
    def captured_group(self,i,j):
        return flood_fill(i,j,self.board)
    
    def check_for_captures(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == 0:
                    continue
                captured_group = self.captured_group(i,j)
                if captured_group is not None:
                    for (x,y) in captured_group:
                        self.captured_pieces[-self.board[x][y]]+=1   # a player captures an opponent's piece
                        self.board[x][y] = 0

    
    def is_full(self):      # might delete later
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == 0:
                     return False
        return True
                
        
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

def drawPieces(game, screen):
        n = game.n
        for i in range(n):
            for j in range(n):
                #desenha peças do jogador 1
                if j==2 and i==3:  #random test values, replace soon
                    pygame.draw.circle(screen, (0,0,255), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))
                #desenha peças do jogador 2
                if j==1 and i==1:   #random test values, replace soon
                    pygame.draw.circle(screen, (0,150,0), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))
                #desenha quadrados onde não se pode jogar
                if j==0 and i==1:   #random test values, replace soon
                    pygame.draw.rect(screen, (0,0,0), (800*i/n, 800*j/n, 800/n + 1, 800/n + 1))

def drawResult(game, screen):
        if game.end == -1:
            return None
        font = pygame.font.Font('freesansbold.ttf', 32)
        pygame.draw.rect(screen, (0,0,0), (120, 240, 560, 320))
        pygame.draw.rect(screen, (255,255,255), (140, 260, 520, 280))
        if game.end == 0:
            text = font.render("Empate!", True, (0,0,0))
        elif game.end == 1:
            text = font.render("Jogador 1 vence!", True, (0,0,255))
        elif game.end == 2:
            text = font.render("Jogador 2 vence!", True, (0,150,0))
        text_rect = text.get_rect(center=(400, 400))
        screen.blit(text, text_rect)

def mousePos(game):
        click = pygame.mouse.get_pos()   
        i = int(click[0]*game.n/800)
        j = int(click[1]*game.n/800)
        coord=(i,j)
        return coord

def showSelected(game, screen, coord, turn):
        n = len(game.board)
        i=coord[0]
        j=coord[1]
        if game.board[j][i] == turn:
            #desenha as cell possiveis de se jogar do player id
            if turn == 1:
                selectedCellRGB  = (173,216,230) #azul claro
            elif turn == 2:
                selectedCellRGB = (144,238,144) #verde claro
            pygame.draw.rect(screen, selectedCellRGB, (800*i/n + 2, 800*j/n + 2, 800/n - 2 , 800/n - 2))

def executeMov(game, targetCell, turn):
        newBoard = cp.deepcopy(game.board)
        newBoard[targetCell[1]][targetCell[0]] = turn
        #newBoard = check_for_captures(targetCell, newBoard, turn)
        newGame = GameState(newBoard)
        return newGame

def jogo_Humano_Humano(game, screen):
        turn = 1
        clickState = False
        while game.end==-1:
            drawPieces(game, screen)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                #verificar se o jogador está cercado / não tem jogadas possiveis e tem de passar a jogada
                if not game.is_full():
                    #escolher a peça para jogar e as possíveis plays
                    if event.type == pygame.MOUSEBUTTONDOWN and clickState == False:
                        drawBoard(game, screen)
                        coord = mousePos(game)
                        selected = showSelected(game, screen, coord, turn)
                        clickState = True
                        drawPieces(game, screen)

                    #fazer o movimento da jogada
                    elif event.type == pygame.MOUSEBUTTONDOWN and clickState == True:
                        targetCell = mousePos(game)
                        prevBoard = cp.deepcopy(game.board)
                        game = executeMov(game, targetCell, turn)
                        if not (np.array_equal(prevBoard,game.board)):
                            turn = switchPlayer(turn)
                        clickState=False
                        drawBoard(game, screen)
                        drawPieces(game, screen)
                else:
                    game.end = objective_test(game,turn)

            #to display the winner
            while game.end != -1:
                drawResult(game,screen)
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                pygame.display.update()
            pygame.display.update()

def switchPlayer(turn):
        return 3-turn

def objective_test(game,player): #atualizar count
    if np.count_nonzero(game.board==(3-player))==0:
        return player
    if np.count_nonzero(game.board==0) != 0:
                return -1
    if np.count_nonzero(game.board==0) == 0:  
        count_p=np.count_nonzero(game.board==player)
        count_o=np.count_nonzero(game.board==(3-player))
        if count_p > count_o:
            return player
        if count_o > count_p:
            return (3-player)
    return 0
    
    
def initialize_game():
    n = ask_board_size()
    initial_board = np.zeros((n, n))     # initializing an empty board of size (n x n)
    captured_pieces = {1:0, -1:0}        # indicates the amount of pieces captured by each player
    initial_state = GameState(initial_board,1,captured_pieces,0)
    pygame.init()
    screen = setScreen()
    drawBoard(initial_state, screen)
    return initial_state
    
def main():
    initial_state = initialize_game()
        
main()

# black plays first
# black -> 1
# white -> -1
# play ends when both players pass
# implementing positional superko rule?
# limite de jogadas: n*n*2
# definir funcao check_for_captures