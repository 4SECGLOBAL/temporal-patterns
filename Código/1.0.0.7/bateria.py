import random
import DataSet as ds
import PatternComplexo as pc
import DBScan as dbd
import DBScanC as dbc
import AnalisarResultados as ar


def run_test_suite(MAI_DAI):
    # Definindo todos os parâmetros
    registros = [2000000]
    padroes = [2]
    itens = [7]
    repeticoes = [3]
    intervalos = [10, 60, 900]
    
    for registro in registros:
        for padrao in padroes:
            for item in itens:
                for repeticao in repeticoes:
                    for intervalo in intervalos: 
                        # Construindo os parâmetros
                        params = {
                            'registros': registro,
                            'padroes': padrao,
                            'itens': item,
                            'repeticoes': repeticao,
                            'intervalo': intervalo
                        }
                    
                        # Chamando a função com os parâmetros atuais
                        MAI_DAI(params)

def MAI_DAI(params):
        
    registros = params['registros']
    padroes = params['padroes']
    itens = params['itens']
    repeticoes = params['repeticoes']
    intervalo = params['intervalo']

    for k in range(1,2):
#     k = 4
#     if k==k:
        if k < 10:
            m = f"180dias_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_00"+str(k)
            n = f"180dias_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_00"+str(k)+".csv"
        elif 10 <= k < 100:
            m = f"180dias_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_0"+str(k)
            n = f"180dias_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_0"+str(k)+".csv"
        else:
            m = f"180dias_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_"+str(k)
            n = f"180dias_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_"+str(k)+".csv"

#       ===============================================================================        
                                       # MINERAÇÃO #
#       -------------------------------------------------------------------------------
        min_repetitions = 3
        pattern_size = itens
#       -------------------------------------------------------------------------------
        segundos = intervalo
        minutos = 0
        horas = 0
        dias = 0
#       =============================================================================== 
        tempo = segundos + (minutos * 60) + (horas * 3600) + (dias * 86400)
#       ===============================================================================
                                       # SINTETICO #
#       -------------------------------------------------------------------------------
        max_time_between_parts = int(tempo/pattern_size)    # segundos
        num_patterns = padroes
        repetitions = repeticoes
        num_linhas = registros - (padroes*repeticoes*itens)
        eps = 0.5
        confianca = 0.0005
#       -------------------------------------------------------------------------------        
#       ===============================================================================        
                                    # PARÂMETRO DE MEMÓRIA
#       -------------------------------------------------------------------------------
        max_items = 100000
#       _______________________________________________________________________________                        
        
#       ===============================================================================

                                    # SEQUÊNCIA DO PROGRAMA #
                                    
#       ===============================================================================
                                     # Criação do dataset #
#       ===============================================================================
#         ds.main(m,num_linhas)
#       _______________________________________________________________________________

                                # Gerador de padrões sintéticos #
#       _______________________________________________________________________________

#         pc.generate_random_patterns(n, n, num_patterns, repetitions, pattern_size, max_time_between_parts)
        
        patterns = [
                {
                'pattern': """
                5767 => 9108
                985 => 9219
                8937 => 2673
                721 => 4205
                """,
                'repetitions': 7
                }
            ]
#         pc.insert_defined_patterns(n, m+".txt", patterns, max_time_between_parts)
#       _______________________________________________________________________________

                           # Clusterização e busca de padrões #                   
#       _______________________________________________________________________________
        
        if pattern_size < min_repetitions:
            min_repetitions = pattern_size

        dbd.main(n, min_repetitions, tempo, max_items, confianca)

        dbc.main(m, n, max_items, min_repetitions, tempo, tempo, confianca)
#       _______________________________________________________________________________

                               # Análise de Resultados #
#       _______________________________________________________________________________
#         ar.analyze_clusters(m)
#         ar.analyze_data(m, 0, f"Resultado_180dias_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}.txt")
#       _______________________________________________________________________________
if __name__ == "__main__":
#     MAI_DAI(faixa, registros, padroes, itens, repeticoes, intervalo)
    run_test_suite(MAI_DAI)
    

