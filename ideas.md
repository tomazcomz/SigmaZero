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
