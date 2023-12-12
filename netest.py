import Go
from ioannina import Neura

def main():
    go=Go.initialize_game()
    rede=Neura(19,go)
    rede.summary()
    return

main()
