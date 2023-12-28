import pygame
import numpy as np
import copy as cp
from copy import deepcopy
import time
from go.utils import flood_fill,get_captured_territories
from go.inputconverter import *
from ioannina import Neura
from MCTS import MCTS

KOMI = 5.5   # predefined value to be added to white's score


class GameState:
    def __init__(self,board,turn=1,play_idx=0,pass_count=0,previous_boards={1:None, -1:None},empty_positions=None,parent=None):
        self.n = len(board)             # number of rows and columns
        self.board = board
        self.turn = turn                # who's playing next
        self.play_idx = play_idx        # how many overall plays occurred before this state
        self.pass_count = pass_count    # counts the current streak of 'pass' plays
        self.previous_boards = previous_boards     # saves both boards originated by each player's last move
        self.parent=parent
        if empty_positions is None:
            self.empty_positions = set([(x,y) for x in range(self.n) for y in range(self.n)])
        else:
            self.empty_positions = empty_positions   # set that stores every empty position in the current board; it is used to facilitate the determination of possible moves in each game state
        self.end = 0             # indicates if the game has ended ({0,1})
        
    def move(self,i,j):         # placing a piece on the board
        next_board = deepcopy(self.board)
        next_board[i][j] = self.turn
        next_board, next_empty_positions = check_for_captures(next_board, self.turn, self.empty_positions)
        next_previous_boards = deepcopy(self.previous_boards)
        next_previous_boards[self.turn] = deepcopy(next_board)
        next_empty_positions.remove((i,j))
        next_state = GameState(next_board,-self.turn,self.play_idx+1,0,next_previous_boards,next_empty_positions,parent=self)
        return next_state
        
    def pass_turn(self):        # a player chooses to "pass"
        next_previous_boards = deepcopy(self.previous_boards)
        next_previous_boards[self.turn] = deepcopy(self.board)
        next_state = GameState(self.board,-self.turn,self.play_idx+1,self.pass_count+1,next_previous_boards,self.empty_positions,parent=self)
        return next_state
            
    def get_winner(self):       # returns the player with the highest score and the scores
        scores = self.get_scores()
        if scores[1] == scores[-1]:
            return 0, scores    # draw
        elif scores[1] > scores[-1]:
            return 1, scores    # player 1 (black, 1) wins
        else:
            return 2, scores    # player 2 (white, -1) wins
    
    def get_scores(self):      # scoring: captured territories + player's stones + komi
        scores = {1:0, -1:0}
        if self.play_idx == 0:
            captured_territories = {1:0, -1:0}
        else:
            captured_territories = self.captured_territories_count()
        n_stones = self.get_number_of_stones()
        scores[1] += captured_territories[1] + n_stones[1]
        scores[-1] += captured_territories[-1] + n_stones[-1] + KOMI
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
    
    def end_game(self):     # retrieving the winner and the scores and ending the game
        self.end = 1
        self.winner,self.scores = self.get_winner()

    # methods used to run the Monte Carlo Tree Search algorithm
    def create_children(self):   # creating all the possible new states originated from the current game state
        children = []
        for move in check_possible_moves(self):
            i,j=move
            new_state = deepcopy(self)
            new_state.move(i,j)
            children.append(new_state)
        return children
            
    def get_next_state(self,i,j):   # given an action, this method returns the resulting game state
        next_state = deepcopy(self)
        next_state.move(i,j)
        return next_state
            
    def get_value_and_terminated(self,state,i,j):   ################### (not sure if this is correct)
        new_state = self.move(i,j)
        if is_game_finished(new_state):
            return 1, True
        if np.sum(check_possible_moves(new_state))==0:
            return 0, True
        return 0, False
            
# auxiliar methods to implement Go's game logic
def check_for_captures(board, turn, empty_positions:set = set()):   # method that checks for captures, given a board and a turn, and returns the new board
    player_checked = -turn   # the player_checked will have its pieces scanned and evaluated if they're captured or not
    empty_positions = deepcopy(empty_positions)
    n = len(board)
    for i in range(n):
        for j in range(n):
            if board[i][j] != player_checked:
                continue    # only checks for captured pieces of the player who didn't make the last move
            captured_group = flood_fill(i,j,board)
            if captured_group is not None:
                for (x,y) in captured_group:
                    board[x][y] = 0    # updating the board after a capture
                    empty_positions.add((x,y))   # adding the territory of the captured piece as an empty position
    return board, empty_positions   # returning the new board and the new empty positions list

def is_move_valid(state:GameState,i,j):
    return (i,j) in check_possible_moves(state)
    
def check_possible_moves(state: GameState):   # returns all empty positions, excluding the ones that would violate the positional superko rule and the ones that would result in suicide
    possible_moves = deepcopy(state.empty_positions)
    if state.play_idx == 0:
        return possible_moves
    moves_to_be_removed = set()
    for move in possible_moves:
        i,j=move
        # checking if a position is a territory captured by the opponent of the player playing next for each possible move, in order to avoid suicide,
        # and removing moves that would violate the positional superko rule
        if is_suicide(state.board,state.turn,i,j) or violates_superko(state.board,state.turn,state.previous_boards[state.turn],i,j):
            moves_to_be_removed.add(move)
    for move in moves_to_be_removed:
        possible_moves.remove(move)   # removing every move that would cause suicide or violation of the positional superko rule
    return possible_moves

def is_suicide(board,turn,i,j):   # checks if a move would result in a 'suicide'
    new_board = deepcopy(board)
    new_board[i][j] = turn    # playing the move in question in a new board
    new_board, _ = check_for_captures(new_board, turn)    # removing the opponent's captured pieces after the new move
    captured_group = flood_fill(i,j,new_board)  # checking if the position (i,j) would be captured after the new move
    if captured_group is not None:
        return True     # if the position would be captured after the new move, then this move results in a suicide
    return False    # otherwise, this move doesn't result in a suicide, thus being playable
            
def violates_superko(board,turn,previous_board,i,j):   # checks if a move would result in a violation of the ko rule (which is a consequence of the positional superko rule)
    new_board = deepcopy(board)
    new_board[i][j] = turn    # playing the move in question in a new board
    new_board, _ = check_for_captures(new_board, turn)   # removing the opponent's captured pieces after the new move
    if np.array_equal(new_board, previous_board):
        return True   # if this move would result in the same board configuration as this player's previous move, then it would violate the ko rule and, consequently, the positional superko rule
    return False    # otherwise, this move doesn't violate the positional superko rule, thus being playable

def is_game_finished(state: GameState):
    if state.pass_count == 2:    # game ends if both players consecutively pass
        print("Reason for game ending: 2 passes in a row")
        return True
    if state.play_idx >= (state.n**2)*2:    # game ends if n*n*2 plays have occurred
        print(f"Reason for game ending: the limit of {state.n**2} plays was exceeded")
        return True
    return False


# implementing the graphical user interface with pygame 
def setScreen():
    width = 800
    height = 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Go")
    return screen
    
def drawBoard(game: GameState, screen):
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

def drawPieces(game: GameState, screen):
    n = game.n
    for i in range(n):
        for j in range(n):
            # draws black pieces
            if game.board[j][i] == 1:
                pygame.draw.circle(screen, (0,0,0), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))
            # draws white pieces
            elif game.board[j][i]==-1:
                pygame.draw.circle(screen, (255,255,255), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))

def drawResult(game: GameState, screen):
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
    color = {1:"black",2:"white"}
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
        
        
def mousePos(game:GameState):
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
    
def human_v_human(game: GameState, screen,rede: Neura):    # main method that runs a human vs human game and implements a GUI
    turn = 1
    m=rede.name
    t=time.time()
    step=0
    while game.end==0:
        drawBoard(game, screen)
        drawPieces(game, screen)
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            game.end==game.get_winner()

        if event.type == pygame.KEYDOWN:    # tecla P = dar pass
            if event.key == pygame.K_p:
                game = game.pass_turn()
            if is_game_finished(game):
                game.end_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            targetCell = mousePos(game)
            prevBoard = cp.deepcopy(game.board)
            i,j = targetCell[1],targetCell[0]
            if not is_move_valid(game,i,j):    # checks if move is valid
                continue    # if not, it expects another event from the same player
            game = game.move(i,j)
            if not (np.array_equal(prevBoard,game.board)):
                turn = switchPlayer(turn)
            time.sleep(0.1)
            drawBoard(game, screen)
            drawPieces(game, screen)
            if is_game_finished(game):
                game.end_game()
            arr=gen_batch(game)
            #np.savetxt(f'go/convertiontest/{m}_{t}_{step}.txt',arr.reshape(arr.shape[0], -1))
            step+=1
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

def agent_v_agent(game: GameState, alphai: MCTS, alphas: MCTS):
    turn = 1
    while game.end==0:
        if turn==1:
            # i,j = alpha_i.play() 
            pass
        if not is_move_valid(game,i,j):    # checks if move is valid
            continue    # if not, it expects another event from the same player
        turn = switchPlayer(turn)
        game = game.move(i,j)    
        if is_game_finished(game):
            game.end_game()
        #arr=gen_batch(game)
        #np.savetxt(f'go/convertiontest/{m}_{t}_{step}.txt',arr.reshape(arr.shape[0], -1))
        # to display the winner
    if game.end != 0:
        return game.winner
            
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
        
        
if __name__ == "__main__":
    n = ask_board_size()
    initial_board = np.zeros((n, n),dtype=int)     # initializing an empty board of size (n x n)
    initial_state = GameState(initial_board)
    pygame.init()
    screen = setScreen()
    drawBoard(initial_state, screen)
    human_v_human(initial_state, screen)
        

# black plays first
# black -> 1 -> player 1
# white -> -1 -> player 2
# play ends when both players pass
# implementing positional superko rule
# limite de jogadas: n*n*2
# making a move that results in 'suicide' is forbidden