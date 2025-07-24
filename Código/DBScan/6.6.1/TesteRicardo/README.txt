Programa roda em chunks para evitar estouro de memória ->
	pode ser ajustado o tamanho no arquivo DBScanC
		main()
		{
			max_itens
		}


Programa pega APENAS as sequências encontradas que correspondem aos padrões, não mais
os padrões soltos.

DICA: Como o programa é rodado na maior quantidade de itens que se repetem (max items)
deixar o programa com um tempo grande (eps) e com pouco item (max items), pode ser que
alguns padrões podem ser comidos pela clusterização e pelo algorítimo de blocos.


objetivo: encontrar o MAIOR número de padrões dentro do dataset.