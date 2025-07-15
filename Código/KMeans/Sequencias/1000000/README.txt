Quanto maior o dataset, maior a quantidade de repetições do padrão que deve ter.

Isso acontece por causa do sup mínimo de 0.1, mas pode ser alterado o parâmetro
a qualquer momento. 

talvez aumentar o número de cluster, daí assim reduzindo a massa de itens, aumentando
o numero do suporte. (mal escrito).


teste 1: 0.1 sup com 100 K
-> nenhum padrão encontrado

teste 2: 0.001 sup com 100 K
-> suposição/hipótese: vai encontrar muitos outros padrões, além dos inseridos.
padrões falsos, com pouca repetição (se abaixar demais, ele pode pegar qualquer coisa
com umas 2 repetições.

demorou demais -> pelas contas, ele daria, no último cluster, cerca de 1 repetição
para estabeler como padrão.

teste 3: 0.005 sup com 100 K
-> 5 repetições (11:45h)