import numpy as np
import socket
import time
from Go import GameState as Go, check_possible_moves, is_game_finished
from go.utils import flood_fill,get_captured_territories


games = ["A4x4", "A5x5", "A6x6", "G7x7", "G9x9"]
game = games[0]


def is_valid_move_go(game,i,j):    # implementing the logic to check if the move is valid
    return (i,j) in check_possible_moves(game)

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

    agents = [agent1, agent2]
    current_agent = 0

    jog=0
    
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
                i = str(data[5])
                j = str(data[7])
                print(current_agent, " -> ",data)
                jog = jog+1
                
                # checking if the move is valid and, if so, executing it
                if is_valid_move_go(GameState,i,j):
                    agents[current_agent].sendall(b'VALID')
                    agents[1-current_agent].sendall(data.encode())
                    GameState = GameState.move(i,j)
                else:
                    agents[current_agent].sendall(b'INVALID')
                
            # checking if the game is over
            if is_game_finished(GameState):
                GameState.end_game()
                winner = GameState.winner
                p1_score = GameState.scores[1]
                p2_score = GameState.scores[-1]
                data = "END " + str(winner) + " " + str(p1_score) + " " + str(p2_score)
                agents[current_agent].sendall(data.encode())
                agents[1-current_agent].sendall(data.encode())
                break
                
            # Switch to the other agent
            current_agent = 1-current_agent
            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            break

    print("\n-----------------\nGAME END\n-----------------\n")
    time.sleep(1)
    agent1.close()
    agent2.close()
    server_socket.close()


def start_server_attaxx():
    pass


if __name__ == "__main__":
    if game[0]=='G':
        start_server_go()
    elif game[0]=='A':
        start_server_attaxx()