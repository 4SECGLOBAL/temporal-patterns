import random
import DataSet as ds
import PatternComplexo as pc
import DBScanC as dbc

def MAI_DAI():
    for k in range(1, 2):
        
#       ===============================================================================
                                       # SINTETICO #
#       -------------------------------------------------------------------------------
        num_linhas = random.randint(90000, 99999)
        num_patterns = 1
        repetitions = 5
        pattern_size = 3
        max_time_between_parts = 15    # minutos
#       ===============================================================================        
                                    # PARÂMETRO DE MEMÓRIA
#       -------------------------------------------------------------------------------
        max_items = 20000
#       ===============================================================================        
                                       # MINERAÇÃO #
#       -------------------------------------------------------------------------------
        min_repetitions = 5
        eps = 3600                      # segundos
#       ===============================================================================    
        n = "00"+str(k)
        
#       Criação do dataset

#         ds.main(n,num_linhas)
        n = "00"+str(k)+".csv"
        
        
#       Gerador de padrões sintéticos

#         pc.generate_random_patterns(n, n, num_patterns, repetitions, pattern_size, max_time_between_parts)

        
#       Clusterização e busca de padrões

        dbc.main(n, max_items, min_repetitions, eps)

if __name__ == "__main__":
    MAI_DAI()
