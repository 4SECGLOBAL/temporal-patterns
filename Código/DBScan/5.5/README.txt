Em datasets sintéticos, pode-se remover grande parte dos outliers (os que não cabem em
algum cluster (Cluster -1) pois os padrões ficam em "núcleos". Os clusteres formados foram com um episolon de 0,3. Quando se reduz muito o episolon, 
o dbscan começa a danififcar os padrões inseridos, removendo itens que fazem parte da sequência. 

ex: 009.csv
eps = 0.3 removeu 3 padrões inteiros dentro da planilha. 0.4 corrigiu e ele conseguiu
encontrar todos os padrões corretamente. Em algumas amostras, ele remove completamente
todos os itens inseridos. Ainda não sei corretamente qual episolon colocar.
