import pygame
import numpy as np
import copy as cp
from utils import flood_fill,get_captured_territories
from copy import deepcopy


class Game:
    def __init__(self,board):
        self.n = len(board)             # number of rows and columns
        self.board = board
        self.captured_pieces = {"p1":0, "p2":0}     # indicates the amount of pieces captured by each player
        self.turn = 1            # who's playing next
        self.play_idx = 0        # how many overall plays occurred before this state
        self.pass_count = 0      # counts the current streak of 'pass' plays
        self.komi = 5.5          # predefined value to be added to white's score
        self.end = 0             # indicates if the game has ended ({0,1})
        self.previous_moves = {"p1":None, "p2":None}     # saves the previous move of each player
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
       
    def is_game_finished(self):
        if self.pass_count == 2:    # game ends if both players consecutively pass
            return True
        if self.play_idx >= self.n*2*2:    # game ends if n*n*2 plays have occurred
            return True
        return False
        
    def get_winner(self):       # returns the player with the highest score or 0, if it's a draw
        scores = self.get_scores()
        print(scores)
        if scores["p1"] == scores["p2"]:
            return 0    # draw
        elif scores["p1"] > scores["p2"]:
            return 1
        else:
            return 2
     
    def get_scores(self):      # scoring: captured territories + player's stones + komi
        scores = {"p1":0, "p2":0}
        captured_territories = self.captured_territories_count()
        n_stones = self.get_number_of_stones()
        scores["p1"] += captured_territories["p1"] + n_stones["p1"]
        scores["p2"] += captured_territories["p2"] + n_stones["p2"] + self.komi
        return scores
    
    def captured_territories_count(self):   # returns how many captured territories each player has
        ct_count = {"p1":0, "p2":0}
        visited = set()     # saves territories that were counted before being visited by the following loops
        for i in range(self.n):
            for j in range(self.n):
                if (i,j) in visited:
                    continue
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
        n_stones = {"p1":0, "p2":0}
        for i in range(self.n):
            for j in range(self.n):
                stone = self.board[i][j]
                if stone == 0:          # if position is empty, the method skips to the next iteration
                    continue
                elif stone == 1:
                    n_stones["p1"] += 1    # increments by one the number of stones for the player who holds this position
                elif stone == -1:
                    n_stones["p2"] += 1
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
        self.end = 1
        self.winner = self.get_winner()
        
def setScreen():
        width = 800
        height = 800
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Go")
        return screen
    
def drawBoard(game, screen):
    screen.fill((117,74,30)) #background castanho

    #desenha frame do tabuleiro
    pygame.draw.line(screen, (0,0,0), (0,0), (800,0), 2)
    pygame.draw.line(screen, (0,0,0), (0,0), (0,800), 2)
    pygame.draw.line(screen, (0,0,0), (0,798), (800,798), 2)
    pygame.draw.line(screen, (0,0,0), (798, 0), (798,800), 2)

    #desenha linhas do tabuleiro
    for i in range(0,game.n):
        #linhas verticais
        pygame.draw.line(screen, (156,113,40), (800*i/game.n + (800/game.n)/2,(800/game.n)/2), (800*i/game.n + (800/game.n)/2 ,800-(800/game.n)/2), 2)
        #linhas horizontais
        pygame.draw.line(screen, (156,113,40), ((800/game.n)/2,800*i/game.n + (800/game.n)/2), (800-(800/game.n)/2,800*i/game.n + (800/game.n)/2), 2)

def drawPieces(game, screen):
        n = game.n
        for i in range(n):
            for j in range(n):
                #desenha peças do jogador 1
                if game.board[j][i] == 1:
                    pygame.draw.circle(screen, (0,0,0), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))
                #desenha peças do jogador 2
                elif game.board[j][i]==-1:
                    pygame.draw.circle(screen, (196,196,196), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))

def drawResult(game, screen):
        if game.end == 0:
            return None
        font = pygame.font.Font('freesansbold.ttf', 32)
        pygame.draw.rect(screen, (0,0,0), (120, 240, 560, 320))
        pygame.draw.rect(screen, (255,255,255), (140, 260, 520, 280))
        result = game.get_winner()
        if result == 0:
            text = font.render("Empate!", True, (0,0,0))
        elif result == 1:
            text = font.render("Jogador 1 vence!", True, (0,0,255))
        elif result == 22:
            text = font.render("Jogador 2 vence!", True, (0,150,0))
        else:
            text = font.render("ERROR", True, (100, 0, 0))
            print(f"Unexpected result: {result}")
        text_rect = text.get_rect(center=(400, 400))
        screen.blit(text, text_rect)

def mousePos(game):
        click = pygame.mouse.get_pos()   
        i = int(click[0]*game.n/800)
        j = int(click[1]*game.n/800)
        coord=(i,j)
        return coord

'''def executeMov(game, targetCell, turn):
        newBoard = cp.deepcopy(game.board)
        newBoard[targetCell[1]][targetCell[0]] = turn
        newGame = GameState(newBoard)
        newGame.turn=switchPlayer(turn)
        newGame.play_idx += 1
        return newGame'''

def jogo_Humano_Humano(game, screen):
        turn = 1
        while game.end==0:
            drawBoard(game, screen)
            drawPieces(game, screen)
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                game.end==game.get_winner()

            if event.type == pygame.KEYDOWN:    # tecla P = dar pass
                if event.key == pygame.K_p:
                    game.pass_turn()

            if event.type == pygame.MOUSEBUTTONDOWN:
                targetCell = mousePos(game)
                prevBoard = cp.deepcopy(game.board)
                game.move(targetCell[1],targetCell[0])
                if not (np.array_equal(prevBoard,game.board)):
                    turn = switchPlayer(turn)
                drawBoard(game, screen)
                drawPieces(game, screen)
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
    initial_board = np.zeros((n, n),dtype=int)     # initializing an empty board of size (n x n)
    initial_state = Game(initial_board)
    pygame.init()
    screen = setScreen()
    drawBoard(initial_state, screen)
    jogo_Humano_Humano(initial_state, screen)
    return initial_state    

def human_vs_human_terminal():
    game_state = initialize_game()
    while game_state.end != 1:
        print(game_state.board)
        print()
        inp = input(f"Player {game_state.turn}'s turn\nChoose your move by entering 'pass' or the coordinates of your move (in the form i,j):\n")
        if inp == "pass":
            game_state.pass_turn()
        else:
            game_state.move(int(inp[0]),int(inp[-1]))
        print()
    winner = game_state.get_winner()
    if winner == 0:
        print("\nGAME OVER\nIt's a draw!")
    else:
        print(f"\nGAME OVER\nPlayer {winner} wins!")


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