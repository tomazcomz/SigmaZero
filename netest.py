from ioannina import Neura
import Attaxx

def main():
    go=Attaxx.main()
    rede=Neura(19,go)
    rede.summary()
    return

main()
