import pygame
import numpy as np
import copy as cp
from go.utils import flood_fill,get_captured_territories
from copy import deepcopy
import time


class Game:
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
        
    def move(self,i,j):         # placing a piece on the board
        self.board[i][j] = self.turn
        self.check_for_captures()
        self.play_idx += 1      # increments the play counter
        self.pass_count = 0     # resets the consecutive pass counter
        self.previous_moves[self.turn] = (i,j)   # saves this move
        self.turn = -self.turn
        self.empty_positions.remove((i,j))
        if self.is_game_finished():
            self.end_game()
        
    def pass_turn(self):        # a player chooses to "pass"
        self.check_for_captures()
        self.play_idx += 1      # increments the play counter
        self.pass_count += 1    # increments the consecutive pass counter
        self.previous_moves[self.turn] = None   # saves this player's move
        self.turn = -self.turn
        if self.is_game_finished():
            self.end_game()
            
    def is_move_valid(self,i,j):
        return (i,j) in self.check_possible_moves()
            
    def check_possible_moves(self):   # returns all empty positions, excluding the ones that would violate the positional superko rule and the ones that would result in suicide
        possible_moves = deepcopy(self.empty_positions)
        prev_move = self.previous_moves[self.turn]
        if prev_move is not None and prev_move in possible_moves:
            possible_moves.remove(prev_move)
        # checking if a position is a territory captured by the opponent of the player playing next for each possible move, in order to avoid suicide
        moves_to_be_removed = set()
        for move in possible_moves:
            i,j=move
            if self.is_suicide(i,j):
                moves_to_be_removed.add(move)
        for move in moves_to_be_removed:
            possible_moves.remove(move)
        return possible_moves
        
    def check_for_captures(self):
        player_checked = -self.turn
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] != player_checked:
                    continue    # only checks for captured pieces of the player who didn't make the last move
                captured_group = self.captured_group(i,j)
                if captured_group is not None:
                    for (x,y) in captured_group:
                        if self.board[x][y]==1:
                            captor = -1
                        elif self.board[x][y]==-1:
                            captor = 1
                        else:
                            raise ValueError("This should be a captured piece")
                        self.captured_pieces[captor]+=1   # a player captures an opponent's piece
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
        if scores[1] == scores[-1]:
            return 0, scores    # draw
        elif scores[1] > scores[-1]:
            return 1, scores    # player 1 (black, 1) wins
        else:
            return 2, scores    # player 2 (white, -1) wins
    
    def get_scores(self):      # scoring: captured territories + player's stones + komi
        scores = {1:0, -1:0}
        captured_territories = self.captured_territories_count()
        n_stones = self.get_number_of_stones()
        scores[1] += captured_territories[1] + n_stones[1]
        scores[-1] += captured_territories[-1] + n_stones[-1] + self.komi
        return scores
     
    def get_number_of_stones(self):     # calculates the number of stones each player has on the board
        n_stones = {1:0, -1:0}
        for i in range(self.n):
            for j in range(self.n):
                stone = self.board[i][j]
                if stone == 0:          # if position is empty, the method skips to the next iteration
                    continue
                n_stones[stone] += 1    # increments by one the number of stones for the player who holds this position
        return n_stones
    
    def captured_territories_count(self):   # returns how many captured territories each player has
        ct_count = {1:0, -1:0}
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
    
    def end_game(self):     # -> code what happens when the game finishes using pygame
        self.end = 1
        self.winner,self.scores = self.get_winner()


def setScreen():
        width = 800
        height = 800
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Go")
        return screen
    
def drawBoard(game, screen):
    screen.fill((220,191,137))    # background

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
            # draws black pieces
            if game.board[j][i] == 1:
                pygame.draw.circle(screen, (0,0,0), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))
            # draws white pieces
            elif game.board[j][i]==-1:
                pygame.draw.circle(screen, (255,255,255), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))

def drawResult(game, screen):
    if game.end == 0:
        return None
    pygame.draw.rect(screen, (0,0,0), (120, 240, 560, 320))
    pygame.draw.rect(screen, (255,255,255), (140, 260, 520, 280))
    font = pygame.font.Font('freesansbold.ttf', 32)
    result,scores = game.winner,game.scores
    if result == 0:
        text = font.render("Draw!", True, (0,0,0))
    elif result == 1 or result == 2:
        result_text(screen,result,scores)
        return
    else:
        text = font.render("ERROR", True, (100, 0, 0))
        print(f"Unexpected result: {result}")
    text_rect = text.get_rect(center=(400, 400))
    screen.blit(text, text_rect)
    
def result_text(screen,result,scores):
    font = pygame.font.Font('freesansbold.ttf', 32)
    color = {1:"white",2:"black"}
    text_lines = [
        "Player " + str(result) + " (" + str(color[result]) + ") wins!",
        "",
        "Score: Black " + str(scores[1]) + " - " + str(scores[-1]) + " White"
    ]
    # Render text surfaces
    text_surfaces = [font.render(line, True, (0,0,0)) for line in text_lines]

    # Calculate text box dimensions
    text_box_width = max(surface.get_width() for surface in text_surfaces)
    text_box_height = sum(surface.get_height() for surface in text_surfaces)

    width,height=800,800
    # Set up text box position
    text_box_x = (width - text_box_width) // 2
    text_box_y = (height - text_box_height) // 2
    
    y_offset = 0
    for surface in text_surfaces:
        screen.blit(surface, (text_box_x, text_box_y + y_offset))
        y_offset += surface.get_height()
        
        
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

def switchPlayer(turn):
    return -turn
    
def human_v_human(game, screen):
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
            i,j = targetCell[1],targetCell[0]
            if not game.is_move_valid(i,j):    # checks if move is valid
                continue    # if not, it expects another event from the same player
            game.move(i,j)
            if not (np.array_equal(prevBoard,game.board)):
                turn = switchPlayer(turn)
            time.sleep(0.1)
            drawBoard(game, screen)
            drawPieces(game, screen)
        # to display the winner
        if game.end != 0:
            drawResult(game,screen)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            pygame.display.update()
            time.sleep(4)
        pygame.display.update()

            
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
        
def initialize_game():
    n = ask_board_size()
    initial_board = np.zeros((n, n),dtype=int)     # initializing an empty board of size (n x n)
    initial_state = Game(initial_board)
    pygame.init()
    screen = setScreen()
    drawBoard(initial_state, screen)
    human_v_human(initial_state, screen)
    return initial_state    


def main():
    initial_state = initialize_game()
        
main()

# black plays first
# black -> 1 -> player 1
# white -> -1 -> player 2
# play ends when both players pass
# implementing positional superko rule
# limite de jogadas: n*n*2
# definir funcao check_for_captures
# definir funcao get_winner