import pygame
import numpy as np
import copy as cp
from utils import flood_fill, get_captured_territories
from copy import deepcopy


class GameState:
    def __init__(self,board):
        self.n = len(board)             # number of rows and columns
        self.board = board
        self.captured_pieces = {1:0, -1:0}     # indicates the amount of pieces captured by each player
        self.turn = 1            # who's playing next
        self.play_idx = 0        # how many overall plays occurred before this state
        self.pass_count = 0      # counts the current streak of 'pass' plays
        self.komi = 5.5          # predefined value to be added to white's score
        self.end = 0             # indicates if the game has ended ({0,1})
        self.previous_moves = {1:None, -1:None}     # saves the previous move of each player
        self.empty_positions = set([(x,y) for x in range(self.n) for y in range(self.n)])    # stores every empty position

    def check_for_captures(self):
        player_checked = -self.turn
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] != player_checked:
                    continue    # only checks for captured pieces of the player who didn't make the last move
                captured_group = self.captured_group(i,j)
                if captured_group is not None:
                    for (x,y) in captured_group:
                        self.captured_pieces[-self.board[x][y]]+=1   # a player captures an opponent's piece
                        self.board[x][y] = 0
                        self.empty_positions.add((x,y))

    # returns None if this position isn't captured, otherwise it returns the positions of the captured group to which (i,j) belongs
    def captured_group(self,i,j):
        return flood_fill(i,j,self.board)
    
    
    def is_full(self):      # might delete later
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == 0:
                    return False
        return True
                
                
    def is_game_finished(self):
        if self.pass_count == 2:    # game ends if both players consecutively pass
            return True
        if self.play_idx >= self.n**2*2:    # game ends if n*n*2 plays have occurred
            return True
        return False
        
    def get_winner(self):       # returns the player with the highest score or 0, if it's a draw
        scores = self.get_scores()
        if scores[-1] == scores[1]:
            return 0    # draw
        return max(scores) 
        return 1 # TEMPORARY
     
    def get_scores(self):      # scoring: captured territories + player's stones + komi
        scores = {1:0, -1:0}
        captured_territories = self.captured_territories_count()
        n_stones = self.get_number_of_stones()
        scores[1] += captured_territories[1] + n_stones[1]
        scores[-1] += captured_territories[-1] + n_stones[-1] + self.komi
        return scores
    
    def captured_territories_count(self):   # returns how many captured territories each player has
        ct_count = {1:0, -1:0}
        visited = set()     # saves territories that were counted before being visited by the following loops
        for i in range(self.n):
            for j in range(self.n):
                piece = self.board[i][j]
                if piece != 0:      # if it's not an empty territory, the method skips to the next iteration
                    continue
                ct_group, captor = get_captured_territories(i,j,self.board)     # gets the group of captured territories this position belongs to and its captor, if there is one
                if ct_group is None:    # if this position isn't part of a group of captured territories, the method skips to the next iteration
                    continue
                for (x,y) in ct_group:
                    visited.add((x,y))      # adding all of the group's position to visited
                    ct_count[captor] += 1   # incrementing the captor's count by one for each captured territory
        return ct_count

    def get_number_of_stones(self):     # calculates the number of stones each player has on the board
        n_stones = {1:0, -1:0}
        for i in range(self.n):
            for j in range(self.n):
                stone = self.board[i][j]
                if stone == 0:          # if position is empty, the method skips to the next iteration
                    continue
                n_stones[stone] += 1    # increments by one the number of stones for the player who holds this position
        return n_stones
    
    def check_possible_moves(self):   # returns all empty positions, excluding the ones that would violate the positional superko rule
        possible_moves = deepcopy(self.empty_positions)
        if self.previous_moves(self.turn) is not None:
            possible_moves.remove(self.previous_moves(self.turn))
        return possible_moves
        
    
    def play(self):     # -> using pygame to choose a move (passing has to be included)
        pass
    
    def move(self,i,j):         # placing a piece on the board
        self.board[i][j] = self.turn
        self.check_for_captures()
        self.play_idx += 1      # increments the play counter
        self.pass_count = 0     # resets the consecutive pass counter
        self.previous_moves[self.turn] = (i,j)
        self.turn = -self.turn
        self.empty_positions.remove((i,j))
        if self.is_game_finished():
            self.end_game()
        
    def pass_turn(self):        # a player chooses to "pass"
        self.play_idx += 1      # increments the play counter
        self.pass_count += 1    # increments the consecutive pass counter
        self.previous_moves[self.turn] = None   # saves this player's move
        self.turn = -self.turn
        if self.is_game_finished():
            self.end_game()
                 
    def end_game(self):     # -> code what happens when the game finishes using pygame
        #####
        self.winner = self.get_winner()
        self.end = 1
    

        
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
        if turn == 1:
            selectedCellRGB  = (173,216,230) #azul claro
        elif turn == -1:
            selectedCellRGB = (144,238,144) #verde claro
        pygame.draw.rect(screen, selectedCellRGB, (800*i/n + 2, 800*j/n + 2, 800/n - 2 , 800/n - 2))

def executeMov(game, targetCell, turn):
        newBoard = cp.deepcopy(game.board)
        newBoard[targetCell[1]][targetCell[0]] = turn
        newGame = GameState(newBoard, switchPlayer(turn), game.captured_pieces, game.play_idx + 1)
        return newGame

def jogo_Humano_Humano(game, screen):
        turn = 1
        clickState = False
        while game.end==0:
            drawBoard(game, screen)
            drawPieces(game, screen)
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                game.end==game.get_winner()
            #verificar se o jogador está cercado / não tem jogadas possiveis e tem de passar a jogada
            if not game.is_full():
                #escolher a peça para jogar e as possíveis plays
                if event.type == pygame.MOUSEBUTTONDOWN and clickState == False:
                    drawBoard(game, screen)
                    coord = mousePos(game)
                    showSelected(game, screen, coord, turn)
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
            while game.end != 0:
                drawResult(game,screen)
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                pygame.display.update()
            pygame.display.update()

def switchPlayer(turn):
        return turn*-1

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


def initialize_game():
    n = ask_board_size()
    initial_board = np.zeros((n, n))     # initializing an empty board of size (n x n)
    initial_state = GameState(initial_board)
    pygame.init()
    screen = setScreen()
    drawBoard(initial_state, screen)
    jogo_Humano_Humano(initial_state, screen)
    return initial_state

def main():
    initial_state = initialize_game()
        
main()

# black plays first
# black -> 1
# white -> -1
# play ends when both players pass
# implementing positional superko rule
# limite de jogadas: n*n*2
# definir funcao check_for_captures
# definir funcao get_winner