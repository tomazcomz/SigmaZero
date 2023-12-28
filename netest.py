from ioannina import Neura
import Attaxx

def main():
    go=Attaxx.main()
    rede=Neura(19,go)
    rede.summary()
    rede2=Neura(39,go)
    rede2.summary()
    return

main()
