A arquitetura de rede neuronal escolhida para os nossos modelos replica a do AlphaZero original que foi proposta por He, Zhang, Ren & Sun no artigo Deep residual learning for image recongnition.
As adaptações que fizemos seguem-se: O número de filters das camadas convolucionais corresponde a 1.7 o quadrado da dimensão do tabuleiro. Este valor foi aproximado primeiramente como a razão entre a dimensão do tabuleiro e número de filtros originais, mas como resulta num número relativamente baixo de parâmetros para os tabuleiros em questão, decidimos optar por esta fórmula para melhor conseguir extrair padrões. O input do Attaxx é bidimensional correspondendo apenas à configuração do tabuleiro, enquanto que o input para o Go é o mesmo do que o originalmente proposto, tendo uma 3 dimensão ao tabuleiro que retém informação sobre as 7 configurações anteriores à apresentada mais própria. Esta conversão é feita em qualquer instante antes de se passar à rede para previsão e os tabuleiros guardados para treino já respeitam este formato. No caso do Attaxx é de notar que exxiste apenas um modelo para qualquer uma das dimensões propostas, isto é conseigo através de usar 8-padding, devido a ser uma célula invalida de jogo, em tabuleiros menores que 6x6 e tendo um modelo que aceita input 6x6.
Nenhuma outra alteração se manteve pelo que a redução de tempo de classificação não escala tanto com o número de blocos convolucionais ou residuais como o número de filtros, pelo que mantemos 19 blocos residuais em qualquer configuração.



Resultados:

O processo de aprendizagem tem sido relativamente atribulado. Primeiramente a exigência computacional de correr uma contidade considerável de jogos contra si mesmos para geração de dados e avaliação de modelo, ainda que a uma escala reduzida. Em termos de jogada, dado o contexto, a velocidade e eficiência parece satisfatória, excepto em casos em que a primeira decisão tomada não seja válida, pelo que na parametrização atual nesses casos não seria possível tomar uma segunda decisão, que se revela pelos resultados empíricos acertada, atempadamente. O modelo go7x7 tem sido a melhor aposta de treino. O modelo de Go9x9 não conseguiria aprender em tempo útil mais do que 3 três iterações do processo, pelo que não foi desenvolvido propriamente. [Attaxx]. 

O historial do modelo de Go segue-se:

    Após cerca de 2 iterações da pipeline, o modelo deixou de aprender. O melhor modelo vigente aprendeu a seguinte tecnica e ficou preso neste mínimo local, o facto de os novos dados serem gerados por este mesmo contribuiu para o problema ainda que houvesse transformação dos trabuleiros para melhor generalização. Posto isto, algumas mudanças foram feitas, como introduzir regularização nas camadas convolucionais e não só nas FC. Tentamos treinar um novo modelo de raiz para ver se derrotaria este persistente. Os resultados foram positivos mas como não ganhava pela margem significativa de superior a 55% ficando sempre nestes 55, não foi substituido.
    Cerca de t-21 horas descobrimos um erro no algoritmo MonteCarlo que põs em causa todo o processo até então e os próprios modelos. Este erro foi corrigido e ... resultados.