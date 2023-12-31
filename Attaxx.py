# This is an adaptation of EIACD's attaxx formulation by Toni-Tomaz

import pygame
from sys import exit
import numpy as np
import copy as cp
import math
import random as rd
import time
from MCTS import *
import optimizar

class GameState:
    def __init__(self, board, player_id=1):
        self.name='attaxx'
        self.player_id = player_id
        self.type=0
        self.board = board
        self.end=-2
        self.children = []
        self.parent = None
        self.parentPlay = None  # (play, movtype)
        self.parentCell = None
    
    def createChildren(self, player_id):
        differentPlayBoards = []
        for i in range(len(self.board)):
            for j in range(len(self.board)):
                if self.board[j][i] == player_id:
                    moves = get_moves(self, (i,j))
                    for mov in moves:
                        if moves[mov][0]:
                            newboard = cp.deepcopy(self.board)
                            play = (i+mov[0], j+mov[1])
                            if moves[mov][1] == 1: #movtype
                                newboard[play[1]][play[0]] = player_id
                            elif moves[mov][1] == 2:
                                newboard[play[1]][play[0]] = player_id
                                newboard[j][i] = 0
                            if newboard not in differentPlayBoards:
                                differentPlayBoards.append(newboard)
                                newboard = get_and_apply_adjacent(play, newboard, player_id)
                                newState = GameState(newboard,-player_id)
                                newState.parentCell = (i,j)
                                newState.parentPlay = (play, moves[mov][1])
                                newState.parent = self
                                self.children.append(newState)
                                
    def switchPlayer(self):
        self.player_id = -self.player_id    

    def check_possible_moves(self):
        possible_moves = set()    # each move is a tuple of coordinates ((initial_cell),(target_cell))
        for i in len(self.board): 
            for j in len(self.board): 
                if self.board[i][j] != self.player_id:
                    continue
                moves_from_a_cell = get_moves(self,(i,j))
                for move in moves_from_a_cell:
                    if move[0]:
                        target_cell = (i+move[0],j+move[1])
                        possible_moves.add(((i,j),target_cell))
        return possible_moves
    
    def is_game_finished(self):
        is_finished,_,_ = _objective_test(self,self.player_id)
        if is_finished  == -2:
            return False
        return True
    

def final_move(game,board,play,player):     #### função que verifica se o estado não tem children
        #print(player,'final')
        gamenp=np.array(board)
        #print(gamenp,'nparray')
        if np.count_nonzero(gamenp==(-player))==0:
            return (True,player)
        if np.count_nonzero(gamenp==(player))==0:
            return (True,-player)
        if np.count_nonzero(gamenp==0) != 0:
            return (False,-2)
        if np.count_nonzero(gamenp==0) == 0:  
            count_p=np.count_nonzero(gamenp==player)
            count_o=np.count_nonzero(gamenp==(-player))
            if count_p > count_o:
                return (True,player)
            if count_o > count_p:
                return (True,-player)
        return (True,0)
    
    #i=y and j=x : tuples are (y,x)
def get_moves(game,cell):
        vect = [(1,0),(2,0),(1,1),(2,2),(1,-1),(2,-2),(-1,0),(-2,0),(-1,1),(-2,-2),(0,1),(0,2),(0,-1),(0,-2),(-1,-1),(-2,2)]
        #moves é um dicionario onde a chave de cada elemento é uma lista com a validade do mov (True/False) no indice 0 e o tipo de movimento no indice 1
        moves={}
        for mov in vect:
            play=(cell[0]+mov[0],cell[1]+mov[1])
            if play[0]<0 or play[0]>len(game.board)-1 or play[1]<0 or play[1]>len(game.board)-1 or game.board[play[1]][play[0]]!=0:
                moves[mov]=[False]
            else:
                moves[mov]=[True]
            if 1 in mov or -1 in mov:
                moves[mov].append(1)
            elif 2 in mov or -2 in mov:
                moves[mov].append(2)
        return moves


    #draws the board on screen
def drawBoard(game: GameState, screen):
        n = len(game.board)
        screen.fill((255,255,255)) #background branco

        #desenha frame do tabuleiro
        pygame.draw.line(screen, (0,0,0), (0,0), (800,0), 2)
        pygame.draw.line(screen, (0,0,0), (0,0), (0,800), 2)
        pygame.draw.line(screen, (0,0,0), (0,798), (800,798), 2)
        pygame.draw.line(screen, (0,0,0), (798, 0), (798,800), 2)

        #desenha linhas do tabuleiro
        for i in range(1,n):
            #linhas verticais
            pygame.draw.line(screen, (0,0,0), (800*i/n,0), (800*i/n,800), 2)
            #linhas horizontais
            pygame.draw.line(screen, (0,0,0), (0,800*i/n), (800,800*i/n), 2)

def drawPieces(game, screen):
        n = len(game.board)
        for i in range(n):
            for j in range(n):
                #desenha peças do jogador 1
                if game.board[j][i] == 1:
                    pygame.draw.circle(screen, (0,0,255), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))
                #desenha peças do jogador 2
                if game.board[j][i] == -1:
                    pygame.draw.circle(screen, (0,150,0), ((800*i/n)+800/(2*n), (800*j/n)+800/(2*n)), 800/(3*n))
                #desenha quadrados onde não se pode jogar
                if game.board[j][i] == 8:
                    pygame.draw.rect(screen, (0,0,0), (800*i/n, 800*j/n, 800/n + 1, 800/n + 1))

    #mostrar o resultado do jogo graficamente
def drawResult(game, screen):
        if game.end == -2:
            return None
        font = pygame.font.Font('freesansbold.ttf', 32)
        pygame.draw.rect(screen, (0,0,0), (120, 240, 560, 320))
        pygame.draw.rect(screen, (255,255,255), (140, 260, 520, 280))
        if game.end == 0:
            text = font.render("Empate!", True, (0,0,0))
        elif game.end == 1:
            text = font.render("Jogador 1 vence!", True, (0,0,255))
        elif game.end == -1:
            text = font.render("Jogador 2 vence!", True, (0,150,0))
        text_rect = text.get_rect(center=(400, 400))
        screen.blit(text, text_rect)

    #return the coordinates of the mouse in the game window
def mousePos(game: GameState):
        click = pygame.mouse.get_pos()   
        n = len(game.board)
        i = int(click[0]*n/800)
        j = int(click[1]*n/800)
        coord=(i,j)
        return coord

    #shows the selected cell on screen
def showSelected(game: GameState, screen, coord, player_id):
        n = len(game.board)
        i=coord[0]
        j=coord[1]
        #selectedType é um dicionario onde cada elemento é um dos quadrados onde se pode jogar e cuja chave é o tipo de movimento
        selectedType = {}
        if game.board[j][i] == player_id:
            #desenha as cell possiveis de se jogar do player id
            if player_id == 1:
                selectedCellRGB  = (173,216,230) #azul claro
            elif player_id == -1:
                selectedCellRGB = (144,238,144) #verde claro
            pygame.draw.rect(screen, selectedCellRGB, (800*i/n + 2, 800*j/n + 2, 800/n - 2 , 800/n - 2))
            moves=get_moves(game,coord)
            for mov in moves:
                if moves[mov][0]:
                    play=(coord[0]+mov[0],coord[1]+mov[1])
                    selectedType[play] = moves[mov][1]
                    pygame.draw.rect(screen, selectedCellRGB, (800*play[0]/n + 2, 800*play[1]/n + 2, 800/n - 2 , 800/n - 2))
        return selectedType

def get_and_apply_adjacent(targetCell, newBoard, player_id):
        vectors = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        #adjacent é um dicionario que vai ter como elemento cada cell que esta a volta da targetCell e cujos elementos sao True/False
        #se essa cell tiver/não tiver uma peça do oponente
        adjacent = {}
        for vect in vectors:
            play=(targetCell[0]+vect[0],targetCell[1]+vect[1])
            if play[0]<0 or play[0]>len(newBoard)-1 or play[1]<0 or play[1]>len(newBoard)-1 or newBoard[play[1]][play[0]] != -player_id:
                adjacent[vect] = False
            else:
                adjacent[vect] = True
        for adj in adjacent:
            if adjacent[adj]:
                adjCell = (targetCell[0]+adj[0], targetCell[1]+adj[1])
                newBoard[adjCell[1]][adjCell[0]] = player_id
        return newBoard

def skip(game: GameState, player):
        game.createChildren(player)
        if len(game.children) == 0:
            return True
        return False
    
def moveGUI(game, initialCell, targetCell, selectedType, player_id):   # used when playing with GUI
        newBoard = cp.deepcopy(game.board)
        if targetCell in selectedType:
            movType = selectedType[targetCell]
            #movimento tipo 1
            if movType == 1:
                newBoard[targetCell[1]][targetCell[0]] = player_id
                newBoard = get_and_apply_adjacent(targetCell, newBoard, player_id)
            #movimento tipo 2
            elif movType == 2:
                newBoard[targetCell[1]][targetCell[0]] = player_id
                newBoard[initialCell[1]][initialCell[0]] = 0
                newBoard = get_and_apply_adjacent(targetCell, newBoard, player_id)
        newGame = GameState(newBoard, -player_id)
        return newGame

def move(game: GameState,initialCell,targetCell,player_id):  # without GUI
    newBoard = cp.deepcopy(game.board)
    moves = get_moves(game,initialCell)
    move = (targetCell[0]-initialCell[0], targetCell[1]-initialCell[1])
    move_type = moves[move][1]
    if move_type == 1:
        newBoard[targetCell[1]][targetCell[0]] = player_id
        newBoard = get_and_apply_adjacent(targetCell, newBoard, player_id)
    elif move_type == 2:
        newBoard[targetCell[1]][targetCell[0]] = player_id
        newBoard[initialCell[1]][initialCell[0]] = 0
        newBoard = get_and_apply_adjacent(targetCell, newBoard, player_id)
    newGame = GameState(newBoard, -player_id)
    return newGame


    #game mode Human vs Human
def jogo_Humano_Humano(game, screen):
        player_id = 1
        clickState = False
        while game.end==-2:
            drawPieces(game, screen)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                #verificar se o jogador está cercado / não tem jogadas possiveis e tem de passar a jogada
                if not skip(game,player_id):
                    #escolher a peça para jogar e as possíveis plays
                    if event.type == pygame.MOUSEBUTTONDOWN and clickState == False:
                        drawBoard(game, screen)
                        coord = mousePos(game)
                        selected = showSelected(game, screen, coord, player_id)
                        clickState = True
                        drawPieces(game, screen)

                    #fazer o movimento da jogada
                    elif event.type == pygame.MOUSEBUTTONDOWN and clickState == True:
                        targetCell = mousePos(game)
                        game = moveGUI(game, coord, targetCell, selected, player_id)
                        player_id = game.player_id
                        clickState=False
                        drawBoard(game, screen)
                        drawPieces(game, screen)
                else:
                    game.switchPlayer()
                    player_id = game.player_id
            game.end = objective_test(game,player_id)

            #to display the winner
            while game.end != -2:
                drawResult(game,screen)
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                pygame.display.update()
            pygame.display.update()

def jogo_Agente_Agente(game, alphai, alphas, sp=False):
    player_id = 1
    labellist=[]
    while game.end==-2:
        if player_id==1:
            action = coord_to_move(game,alphai.play())
        else:
            action=coord_to_move(game,alphas.play())
        if action not in game.check_possible_moves():    # checks if move is valid
            continue    # if not, it expects another event from the same player
        player_id = -player_id
        game = move(game, action[0], action[1], player_id)
        if game.is_game_finished():
            game.end=objective_test(game, player_id)
        if (sp):
            fname=optimizar.sptrainprocd(game.board,alphas.name)
            labellist.append(fname)
         # to display the winner
    if game.end != -2:
        if sp:
            optimizar.labelmaking(labellist,game.end)
        return game.end

def convert_to_six_by_six(board):
        if len(board) == 4:
            newboard = [[8,8,8,8,8,8]]
            for i in range(len(board)):
                line = [8]
                for j in range(len(board)):
                    line.append(board[i][j])
                line.append(8)
                newboard.append(line)
            newboard.append([8,8,8,8,8,8])
            return newboard
        elif len(board) == 5:
            newboard=[]
            for i in range(len(board)):
                line = [8]
                for j in range(len(board)):
                    line.append(board[i][j])
                newboard.append(line)
            newboard.append([8,8,8,8,8,8])
            return newboard
        else:
            return board

def coord_to_move(game, targetCell):
       possible_origins = set()
       for move in game.check_possible_moves():
            if move[1]==targetCell:
                possible_origins.add(move[0])
                if abs(move[0][0]-targetCell[0])==1 or abs(move[0][1]-targetCell[1])==1:
                    return (move[0],targetCell)
       return (possible_origins.pop(),targetCell)

def objective_test(game: GameState,player):   # atualizar count (com GUI)
    gamenp=np.array(game.board)
    if np.count_nonzero(gamenp==(-player))==0:
        return player
    if np.count_nonzero(gamenp==0) != 0:
        return -2
    if np.count_nonzero(gamenp==0) == 0:  
        count_p=np.count_nonzero(gamenp==player)
        count_o=np.count_nonzero(gamenp==(-player))
        if count_p > count_o:
            return player
        if count_o > count_p:
            return (-player)
    return 0

def _objective_test(game: GameState,player):   # devolve também as pontuações
    gamenp=np.array(game.board)
    if np.count_nonzero(gamenp==(-player))==0:
        return player,len(gamenp),0
    if np.count_nonzero(gamenp==0) != 0:
        return -2,-2,-2
    if np.count_nonzero(gamenp==0) == 0:  
        count_p=np.count_nonzero(gamenp==player)
        count_o=np.count_nonzero(gamenp==(-player))
        if count_p > count_o:
            return player, count_p, count_o
        if count_o > count_p:
            return (-player), count_o, count_p
    return 0, count_p, count_o


def setScreen():
        width = 800
        height = 800
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Ataxx")
        return screen

    #abre um ficheiro com um mapa do tabuleiro a ser usado no jogo e cria o estado/objeto inicial
def readBoard(ficheiro):
        f = open(ficheiro, "r")
        n = int(f.readline())
        board = []
        for i in range(n):
            board.append(list(map(int, f.readline().split())))
        f.close()
        return GameState(board)

    #pede ao user para escolher o tabuleiro que pretende usar
def chooseBoard(tableNum=None):
        #todos os ficheiros com tabuleiros devem ter nome do tipo "tabX.txt"
        if tableNum==None:
            tableNum = input("Escolha o número do tabuleiro que quer usar para o jogo!\n4) 4x4\n6) 6x6\nTabuleiro: ")
        table = "attaxx/tab"+tableNum+".txt"
        return table
   
if __name__ == "__main__":
    start_time = time.time()
    table = chooseBoard()
    pygame.init()
    screen = setScreen()
    game = readBoard(table)
    drawBoard(game, screen)
    jogo_Humano_Humano(game, screen)
    print("--- %.5f seconds ---" % (time.time() - start_time))

def create(size=None):
    table = chooseBoard(size)
    game = readBoard(table)
    return game