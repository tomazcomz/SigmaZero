Game Agnostic Implementation

(learning to play othello without human knowledge)
'Setting τ to a high value gives us almost uniform distribution, while setting it to 0 makes us always select the best action'
'In our experiments, the temperature parameter τ is set to 1 for the first 25 turns in an episode, to encourage early exploration, and then set to 0. It is always set to 0 during evaluation.'  

basic joseki video:
https://youtu.be/GGTbb-_ZWT8?si=4Ylsi0j_EzwQYzKC

Self/Opponent vs Black/White
<img width="501" alt="image" src="https://github.com/tomazcomz/SigmaZero/assets/125892880/1565ce0f-ad0a-45df-a1f7-cf25326a2ec7">

Tromp-Taylor rules
concisas: https://webdocs.cs.ualberta.ca/~hayward/396/hoven/tromptaylor.pdf
explicadas com exemplos: https://webdocs.cs.ualberta.ca/~hayward/355/gorules.pdf

"Go is well suited to the neural network architecture used in AlphaGo because the rules of
the game are translationally invariant (matching the weight sharing structure of convolutional
networks), are defined in terms of liberties corresponding to the adjacencies between points
on the board (matching the local structure of convolutional networks), and are rotationally and
reflectionally symmetric (allowing for data augmentation and ensembling). Furthermore, the
action space is simple (a stone may be placed at each possible location), and the game outcomes
are restricted to binary wins or losses, both of which may help neural network training."  - talvez usar numpy array para a eventualidade de inverter/rodar matrizes

quando se da input de um estado à rede neuronal, dar tambem input as suas rotacoes e simetrias

"Go is well suited to the neural network architecture used in AlphaGo because the rules of
the game are translationally invariant (matching the weight sharing structure of convolutional
networks), are defined in terms of liberties corresponding to the adjacencies between points
on the board (matching the local structure of convolutional networks), and are rotationally and
reflectionally symmetric (allowing for data augmentation and ensembling). Furthermore, the
action space is simple (a stone may be placed at each possible location), and the game outcomes
are restricted to binary wins or losses, both of which may help neural network training."  - talvez usar numpy array para a eventualidade de inverter/rodar matrizes

quando se da input de um estado à rede neuronal, dar tambem input as suas rotacoes e simetrias

# Poupar Tempo:

    - Usar Java em TreeSearch
    - Tirar PyGame e prints

# MCTS:
    
    - Não excluir jogadas legais nem as que são postas nos 'eyes' do próprio jogador
    - Parâmetros do MCTS são inicializados por otimização Gaussiana : 'so as to optimizeselfplay performance of AlphaGo Zero using a neural network trained in apreliminary run. For the larger run (40 blocks, 40 days), MCTS search parameters were reoptimized using the neural network trained in the smaller run(20 blocks, 3 days)'
    - APV-MCTS (ver resto destacado no pdf do paper original)
    - "The original paper mentions that Dirichlet noise is added to prior probabilities for additional exploration in the self-play stage"