import random
import DataSet as ds
import PatternComplexo as pc
import DBScanC as dbc
import AnalisarResultados as ar

def MAI_DAI():
#     for k in range(1,11):
    k = 1
    if k==k:
        if k < 10:
            m = "00"+str(k)
            n = "00"+str(k)+".csv"
        elif 10 <= k < 100:
            m = "0"+str(k)
            n = "0"+str(k)+".csv"
        else:
            m = str(k)
            n = str(k)+".csv"

#       ===============================================================================        
                                       # MINERAÇÃO #
#       -------------------------------------------------------------------------------
        min_repetitions = 5
        confianca = 0.05
        pattern_size = 7
#       -------------------------------------------------------------------------------
        segundos = 0
        minutos = 120
        horas = 0
        dias = 0
#       =============================================================================== 
        tempo = segundos + (minutos * 60) + (horas * 3600) + (dias * 86400)
#       ===============================================================================
                                       # SINTETICO #
#       -------------------------------------------------------------------------------
        max_time_between_parts = int(tempo/pattern_size)    # minutos
        num_linhas = random.randint(500, 501)
        num_patterns = 1
        repetitions = 5
        eps = 0.5
#       -------------------------------------------------------------------------------        
#       ===============================================================================        
                                    # PARÂMETRO DE MEMÓRIA
#       -------------------------------------------------------------------------------
        max_items = 30000
#       _______________________________________________________________________________                        
        
#       ===============================================================================

                                    # SEQUÊNCIA DO PROGRAMA #
                                    
#       ===============================================================================
                                     # Criação do dataset #
#       ===============================================================================

        ds.main(m,num_linhas)
#       _______________________________________________________________________________

                                # Gerador de padrões sintéticos #
#       _______________________________________________________________________________

        pc.generate_random_patterns(n, n, num_patterns, repetitions, pattern_size, max_time_between_parts)

        patterns = [
                {
                'pattern': """
                5767 => 9108
                985 => 9219
                8937 => 2673
                """,
                'repetitions': 6
                }
            ]
#         pc.insert_defined_patterns(n, m+"_1.txt", patterns, max_time_between_parts)

        patterns = [
                {
                'pattern': """
                3845 => 1951
                405 => 7600
                1732 => 6455
                """,
                'repetitions': 3 
                }
            ]

#         pc.insert_defined_patterns(n, m+"_2.txt", patterns, max_time_between_parts)        
        patterns = [
            {
            'pattern': """
            8269 => 1482
            4758 => 745
            7598 => 7548
            """,
            'repetitions': 3 
            }
        ]
#         pc.insert_defined_patterns(n, m+"_3.txt", patterns, max_time_between_parts)

#       _______________________________________________________________________________

                           # Clusterização e busca de padrões #                   
#       _______________________________________________________________________________
        
        if pattern_size < min_repetitions:
            min_repetitions = pattern_size
            
        dbc.main(m, n, max_items, min_repetitions, tempo, tempo, confianca)
#       _______________________________________________________________________________

                               # Análise de Resultados #
#       _______________________________________________________________________________
        ar.analyze_clusters(m)
        ar.analyze_data(m, 0, "Resultado.txt")
#       _______________________________________________________________________________
if __name__ == "__main__":
    MAI_DAI()
    