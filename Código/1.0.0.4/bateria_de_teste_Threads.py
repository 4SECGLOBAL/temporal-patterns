import threading
from queue import Queue
import random
import DataSet as ds
import PatternComplexo as pc
import DBScanC as dbc
import AnalisarResultados as ar

def MAI_DAI(registros, padroes, itens, repeticoes, intervalo):
# def MAI_DAI(params):
    for k in range(1,11):
#     k = 4
#     if k==k:
        if k < 10:
            m = f"{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_00"+str(k)
            n = f"{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_00"+str(k)+".csv"
        elif 10 <= k < 100:
            m = f"{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_0"+str(k)
            n = f"{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_0"+str(k)+".csv"
        else:
            m = f"{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_"+str(k)
            n = f"{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_"+str(k)+".csv"

#       ===============================================================================        
                                       # MINERAÇÃO #
#       -------------------------------------------------------------------------------
        min_repetitions = repeticoes
        confianca = 0.05
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
        pattern_size = itens
        max_time_between_parts = int(tempo/pattern_size)    # minutos
        num_linhas = registros
        num_patterns = padroes
        repetitions = repeticoes
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
            
        dbc.main(m, n, max_items, min_repetitions, tempo, tempo)
#       _______________________________________________________________________________

                               # Análise de Resultados #
#       _______________________________________________________________________________
        ar.analyze_clusters(m)
        ar.analyze_data(m, 0, f"Resultado_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}.txt")
#       _______________________________________________________________________________

def run_test_suite_threaded(MAI_DAI):
    # Tarefa I. configuração das threads
    threads_config = [
        {
            'name': 'Thread 1 (500-10000)',
            'registros': [500, 2000, 5000, 10000],
            'padroes': [1, 2, 3, 4, 5],
            'itens': [3, 4, 5, 6, 7],
            'repeticoes': [3, 4, 5, 6, 7],
            'intervalo': [5, 10, 30, 60, 120, 180]
        },
        {
            'name': 'Thread 2 (50000)',
            'registros': [50000],
            'padroes': [1, 2, 3, 4, 5],
            'itens': [3, 4, 5, 6, 7],
            'repeticoes': [3, 4, 5, 6, 7],
            'intervalo': [5, 10, 30, 60, 120, 180]
        },
        {
            'name': 'Thread 3 (100000 - padrões 1-3)',
            'registros': [100000],
            'padroes': [1, 2, 3],
            'itens': [3, 4, 5, 6, 7],
            'repeticoes': [3, 4, 5, 6, 7],
            'intervalo': [5, 10, 30, 60, 120, 180]
        },
        {
            'name': 'Thread 4 (100000 - padrões 4-5)',
            'registros': [100000],
            'padroes': [4, 5],
            'itens': [3, 4, 5, 6, 7],
            'repeticoes': [3, 4, 5, 6, 7],
            'intervalo': [5, 10, 30, 60, 120, 180]
        },
        {
            'name': 'Thread 5 (200000 - padrão 1)',
            'registros': [200000],
            'padroes': [1],
            'itens': [3, 4, 5, 6, 7],
            'repeticoes': [3, 4, 5, 6, 7],
            'intervalo': [5, 10, 30, 60, 120, 180]
        },
        {
            'name': 'Thread 6 (200000 - padrão 2)',
            'registros': [200000],
            'padroes': [2],
            'itens': [3, 4, 5, 6, 7],
            'repeticoes': [3, 4, 5, 6, 7],
            'intervalo': [5, 10, 30, 60, 120, 180]
        },
        {
            'name': 'Thread 7 (200000 - padrão 3)',
            'registros': [200000],
            'padroes': [3],
            'itens': [3, 4, 5, 6, 7],
            'repeticoes': [3, 4, 5, 6, 7],
            'intervalo': [5, 10, 30, 60, 120, 180]
        },
        {
            'name': 'Thread 8 (200000 - padrão 4)',
            'registros': [200000],
            'padroes': [4],
            'itens': [3, 4, 5, 6, 7],
            'repeticoes': [3, 4, 5, 6, 7],
            'intervalo': [5, 10, 30, 60, 120, 180]
        },
        {
            'name': 'Thread 9 (200000 - padrão 5)',
            'registros': [200000],
            'padroes': [5],
            'itens': [3, 4, 5, 6, 7],
            'repeticoes': [3, 4, 5, 6, 7],
            'intervalo': [5, 10, 30, 60, 120, 180]
        }
    ]

    # Tarefa II. criando fila para logística
    results_queue = Queue()
    threads = []

    def thread_worker(config, MAI_DAI, queue):
        try:
            for registro in config['registros']:
                for padrao in config['padroes']:
                    for item in config['itens']:
                        for repeticao in config['repeticoes']:
                            for intervalo_val in config['intervalo']:
                                params = {
                                    'registros': registro,
                                    'padroes': padrao,
                                    'itens': item,
                                    'repeticoes': repeticao,
                                    'intervalo': intervalo_val
                                }
#                                 print(f"{config['name']} executando: {params}")
                                MAI_DAI(**params)
#                                 queue.put(f"{config['name']} completou: {params}")
        except Exception as e:
            queue.put(f"ERRO em {config['name']}: {str(e)}")

    # Tarefa III. criar e iniciar as threads
    for config in threads_config:
        thread = threading.Thread(
            target=thread_worker,
            args=(config, MAI_DAI, results_queue),
            name=config['name']
        )
        threads.append(thread)
        thread.start()

    # Tarefa III.I. Monitoramento
    def monitor_progress():
        while any(t.is_alive() for t in threads):
            while not results_queue.empty():
                print(results_queue.get())
            # Verifica a cada 5 segundos
            threading.Event().wait(5)

    monitor_thread = threading.Thread(target=monitor_progress)
    monitor_thread.start()

    # Tarefa IV. aguardar todas as threads terminarem
    for thread in threads:
        thread.join()

    monitor_thread.join()

    print("\n=== RESULTADOS FINAIS ===")
    while not results_queue.empty():
        print(results_queue.get())

if __name__ == "__main__":
    run_test_suite_threaded(MAI_DAI)
