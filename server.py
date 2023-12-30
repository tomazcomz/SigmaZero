import numpy as np
import socket
import time
from Go import GameState as Go, check_possible_moves, is_game_finished as is_game_finished_go, setScreen as set_screen_go, drawBoard as draw_board_go, drawPieces as draw_pieces_go, drawResult as draw_result_go
from Attaxx import GameState as Attaxx, _executeMov as execute_move, _objective_test as is_game_finished_attaxx, get_moves, setScreen as set_screen_attaxx, drawBoard as draw_board_attaxx, drawPieces as draw_pieces_attaxx, drawResult as draw_result_attaxx
import pygame

games = ["A4x4", "A5x5", "A6x6", "G7x7", "G9x9"]
# game = games[0]     # ATTAXX
game = games[3]     # GO

def is_move_valid_go(game,move):    # implementing the logic to check if the move is valid
    return move in check_possible_moves(game)

def start_server_go(host='localhost', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)

    print("Waiting for two agents to connect...")
    agent1, addr1 = server_socket.accept()
    print("Agent 1 connected from", addr1)
    bs=b'AG1 '+game.encode()
    agent1.sendall(bs)

    agent2, addr2 = server_socket.accept()
    print("Agent 2 connected from", addr2)
    bs=b'AG2 '+game.encode()
    agent2.sendall(bs)
       
    n = int(game[1])
    initial_board = np.zeros((n, n),dtype=int)     # initializing an empty board of size (n x n)
    GameState = Go(initial_board)    # initializing the game
    
    pygame.init()
    screen = set_screen_go()    # setting the screen for graphical display
    draw_board_go(GameState, screen)
    pygame.display.update()

    agents = [agent1, agent2]
    current_agent = 0

    jog=0
    
    time.sleep(3)
    while True:
        try:
            data = agents[current_agent].recv(1024).decode()
            if not data:
                break

            if data == "PASS":
                agents[current_agent].sendall(b'VALID')
                agents[1-current_agent].sendall(data.encode())
                GameState.pass_turn()
            else:
                # processing the move (example: "MOVE X,Y")
                i = int(data[5])
                j = int(data[7])
                if current_agent == 0:
                    print("Agent 1 -> ",data)
                else:
                    print("Agent 2 -> ",data)
                jog = jog+1
                
                # checking if the move is valid and, if so, executing it
                if is_move_valid_go(GameState,(i,j)):
                    agents[current_agent].sendall(b'VALID')
                    agents[1-current_agent].sendall(data.encode())
                    GameState = GameState.move((i,j))
                    time.sleep(0.1)
                    draw_board_go(GameState, screen)
                    draw_pieces_go(GameState, screen)
                    event = pygame.event.poll()
                else:
                    agents[current_agent].sendall(b'INVALID')
                    continue
                
            pygame.display.update()
                
            # checking if the game is over
            if is_game_finished_go(GameState):
                GameState.end_game()
                winner = GameState.winner
                if winner == -1:
                    winner = 2
                p1_score = GameState.scores[1]
                p2_score = GameState.scores[-1]
                data = "END " + str(winner) + " " + str(p1_score) + " " + str(p2_score)
                agents[current_agent].sendall(data.encode())
                agents[1-current_agent].sendall(data.encode())
                draw_result_go(GameState, screen)
                pygame.display.update()
                time.sleep(4)
                pygame.quit()
                break
                
            # Switch to the other agent
            current_agent = 1-current_agent

        except Exception as e:
            print("Error:", e)
            break

    print("\n-----------------\nGAME END\n-----------------\n")
    time.sleep(1)
    agent1.close()
    agent2.close()
    server_socket.close()
    
    
def create_board_attaxx(n):
    board = np.zeros((n, n),dtype=int)
    board[0][0] = board[n-1][n-1] = 1
    board[n-1][0] = board[0][n-1] = -1
    return board

def is_move_valid_attaxx(GameState,i,j,i2,j2):
    possible_moves = [(1,0),(2,0),(1,1),(2,2),(1,-1),(2,-2),(-1,0),(-2,0),(-1,1),(-2,-2),(0,1),(0,2),(0,-1),(0,-2),(-1,-1),(-2,2)]
    move = (i2-i,j2-j)
    if move not in possible_moves:
        return False
    moves = get_moves(GameState,(i,j))
    return moves[move][0]

def start_server_attaxx(host='localhost', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)

    print("Waiting for two agents to connect...")
    agent1, addr1 = server_socket.accept()
    print("Agent 1 connected from", addr1)
    bs=b'AG1 '+game.encode()
    agent1.sendall(bs)

    agent2, addr2 = server_socket.accept()
    print("Agent 2 connected from", addr2)
    bs=b'AG2 '+game.encode()
    agent2.sendall(bs)
       
    n = int(game[1])
    initial_board = create_board_attaxx(n)     # initializing an empty board of size (n x n)
    GameState = Attaxx(initial_board)    # initializing the game

    pygame.init()
    screen = set_screen_attaxx()    # setting the screen for graphical display
    draw_board_attaxx(GameState, screen)
    draw_pieces_attaxx(GameState, screen)
    pygame.display.update()

    agents = [agent1, agent2]
    current_agent = 0
    player_id = 1

    jog=0
    
    time.sleep(3)
    while True:
        try:
            data = agents[current_agent].recv(1024).decode()
            if not data:
                break

            # processing the move (example: "MOVE X,Y,X2,Y2")
            i = int(data[5])
            j = int(data[7])
            i2 = int(data[9])
            j2 = int(data[11])
            if current_agent == 0:
                print("Agent 1 -> ",data)
            else:
                print("Agent 2 -> ",data)
            jog = jog+1
            
            # checking if the move is valid and, if so, executing it
            if is_move_valid_attaxx(GameState,i,j,i2,j2):
                agents[current_agent].sendall(b'VALID')
                agents[1-current_agent].sendall(data.encode())
                GameState = execute_move(GameState,(i,j),(i2,j2),player_id=player_id)
                time.sleep(0.1)
                draw_board_attaxx(GameState, screen)
                draw_pieces_attaxx(GameState, screen)
                event = pygame.event.poll()
            else:
                agents[current_agent].sendall(b'INVALID')
                continue

            pygame.display.update()

            # checking if the game is over
            value,score1,score2 = is_game_finished_attaxx(GameState,player=player_id)   # -1 if game is not over, 0 if it's a draw, 1 if player 1 won and 2 if player 2 won 
            if value != -2:
                result = value
                if result == 1:
                    p1_score = score1
                    p2_score = score2
                else:
                    p2_score = score1
                    p1_score = score2
                data = "END " + str(result) + " " + str(p1_score) + " " + str(p2_score)
                agents[current_agent].sendall(data.encode())
                agents[1-current_agent].sendall(data.encode())
                draw_result_attaxx(GameState, screen)
                pygame.display.update()
                time.sleep(4)
                pygame.quit()
                break
                
            # Switch to the other agent
            current_agent = 1-current_agent
            player_id = 0-player_id

        except Exception as e:
            print("Error:", e)
            break

    print("\n-----------------\nGAME END\n-----------------\n")
    time.sleep(1)
    agent1.close()
    agent2.close()
    server_socket.close()
    
if __name__ == "__main__":
    if game[0]=='G':
        start_server_go()
    elif game[0]=='A':
        start_server_attaxx()