import numpy as np
import socket
import time
from Go import Game as Go


games = ["A4x4", "A5x5", "A6x6", "G7x7", "G9x9"]
game = games[0]


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
    Game = Go(initial_board)    # initializing the game

    agents = [agent1, agent2]
    current_agent = 0

    jog=0
    
    while True:
        try:
            data = agents[current_agent].recv(1024).decode()
            if not data:
                break

            # processing the move (example: "MOVE X,Y")
            i = str(data[5])
            j = str(data[7])
            print(current_agent, " -> ",data)
            jog = jog+1
            
            if jog==10:
                agents[current_agent].sendall(b'END 0 10 10')
                agents[1-current_agent].sendall(b'END 0 10 10')
                break
            
            if Game.is_move_valid(i,j):
                agents[current_agent].sendall(b'VALID')
                agents[1-current_agent].sendall(data.encode())
                Game.move(i,j)
            else:
                agents[current_agent].sendall(b'INVALID')

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


def is_valid_move(move):    # implementing the logic to check if the move is valid
    return True

def start_server_attaxx():
    pass


if __name__ == "__main__":
    if game[0]=='G':
        start_server_go()