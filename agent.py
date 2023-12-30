import socket
import random
import time


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
        return generate_random_move_go()
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

    while True:
        # Generate and send a random move
        if ag == 1 or not first:
            move = choose_move(game_name)
            time.sleep(1)
            client_socket.send(move.encode())
            print("Send:",move)
        
            # Wait for server response
            response = client_socket.recv(1024).decode()
            print(f"Server Response1: {response}")
            if response == "INVALID":
                continue
            if "END" in response: break
            
        first=False
        response = client_socket.recv(1024).decode()
        print(f"Server Response2: {response}")
        if "END" in response: break

    client_socket.close()
    
    
if __name__ == "__main__":
    connect_to_server()