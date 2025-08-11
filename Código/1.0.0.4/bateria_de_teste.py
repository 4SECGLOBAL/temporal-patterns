import random
import DataSet as ds
import PatternComplexo as pc
import DBScanC as dbc
import AnalisarResultados as ar


def run_test_suite(MAI_DAI):
    # Definindo todos os parâmetros baseados na tabela
    registros = [500, 2000, 5000, 10000, 50000, 200000]
    padroes = [1, 2, 3, 4, 5]
    itens = [3, 4, 5, 6, 7]
    repeticoes = [3, 4, 5, 6, 7]
    intervalo = [5, 10, 30, 60, 120, 180]
    
    for timeframe in time_frames:
        for record in records:
            for pattern in patterns:
                for repetition in repetitions:
                    # Construindo os parâmetros
                    params = {
                        'registros': registros,
                        'padrões': padroes,
                        'itens': itens,
                        'repetições': repeticoes,
                        'intervalo': intervalo
                    }
                    
                    # Chamando a função com os parâmetros atuais
                    print(f"Testando: {params}")
                    MAI_DAI(params)

def MAI_DAI(faixa, registros, padroes, itens, repeticoes, intervalo):
    for k in range(1,11):
#     k = 4
#     if k==k:
        if k < 10:
            m = f"{faixa}_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_00"+str(k)
            n = f"{faixa}_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_00"+str(k)+".csv"
        elif 10 <= k < 100:
            m = f"{faixa}_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_0"+str(k)
            n = f"{faixa}_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_0"+str(k)+".csv"
        else:
            m = f"{faixa}_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_"+str(k)
            n = f"{faixa}_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_"str(k)+".csv"

#       ===============================================================================        
                                       # MINERAÇÃO #
#       -------------------------------------------------------------------------------
        min_repetitions = repeticoes
        pattern_size = itens
#       -------------------------------------------------------------------------------
        segundos = 0
        minutos = intervalo
        horas = 0
        dias = 0
#       =============================================================================== 
        tempo = segundos + (minutos * 60) + (horas * 3600) + (dias * 86400)
#       ===============================================================================
                                       # SINTETICO #
#       -------------------------------------------------------------------------------
        max_time_between_parts = int(tempo/pattern_size)    # minutos
        num_linhas = registros
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
        verific = str(input(f"Certifique-se do intervalo de registros no arquivo de dataset. O tempo inserido é: {faixa}.\n "))
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
            
        dbc.main(m, n, max_items, min_repetitions, tempo, tempo)
#       _______________________________________________________________________________

                               # Análise de Resultados #
#       _______________________________________________________________________________
        ar.analyze_clusters(m)
        ar.analyze_data(m, 0, f"Resultado_{faixa}_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}.txt")
#       _______________________________________________________________________________
if __name__ == "__main__":
#     MAI_DAI(faixa, registros, padroes, itens, repeticoes, intervalo)
    run_test_suite(MAI_DAI)
    
