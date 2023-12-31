import socket
import random
import time
import avaliar
from MCTS import MCTS
from ioannina import Neura
import Go,Attaxx


ARGS = {
    'cpuct': 1.5,
    'num_searches': 1600
}


def generate_random_move_attaxx():     # ATTAXX
    x = random.randint(0, 3)
    y = random.randint(0, 3)
    x2 = random.randint(0, 3)
    y2 = random.randint(0, 3)
    return f"MOVE {x},{y},{x2},{y2}"

def generate_random_move_go():     # GO
    x = random.randint(0, 6)
    y = random.randint(0, 6)
    return f"MOVE {x},{y}"

def choose_move_go():
    pass

def choose_move_attaxx():
    pass

def choose_move(game_name):   # returns the move in the form "MOVE X,Y"
    if game_name=='go':
        #return generate_random_move_go()
        return choose_move_go()
    else:
        return generate_random_move_attaxx()
        return choose_move_attaxx()
    
    
def connect_to_server(host='localhost', port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    response = client_socket.recv(1024).decode()
    print(f"Server ResponseINIT: {response}")

    Game = response[-4:]
    print("Playing:", Game)
    if Game[0]=='A':
        game_name = 'attaxx'
    else:
        game_name = 'go'
    n = int(Game[1])

    if "1" in response:
        ag=1
    else:
        ag=2
    first=True

    game_state=avaliar.makegame(Game)
    teta=Neura(game_state)
    teta.net.load_weights()
    alpha=MCTS(game_state,ARGS,teta)

    while True:
        # Generate and send a random move
        if ag == 1 or not first:
            move = alpha.play()
            time.sleep(1)
            smove=str(move)
            client_socket.send(smove.encode())
            print("Send:",move)
        
            # Wait for server response
            response = client_socket.recv(1024).decode()
            print(f"Server Response1: {response}")
            if response == "INVALID":
                continue
            if "END" in response: break
            game_state=game_state.move(move)
            
        first=False
        response = client_socket.recv(1024).decode()
        if response == "PASS":
            game_state = game_state.pass_turn()
        else:
            i=response[5]
            j=response[7]
            if game_name == "attaxx":
                i2=response[9]
                j2=response[11]
        action=(int(i),int(j))
        print(f"Server Response2: {response}")
        if "END" in response: break
        game_state=game_state.move(action)
        alpha.cut(action)

    client_socket.close()
    
    
if __name__ == "__main__":
    connect_to_server()