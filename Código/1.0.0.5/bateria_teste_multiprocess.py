# bateria_teste_multiprocess.py  (pode manter o nome original, mas recomendo este)
import os
# Limitar threads internas de BLAS/NumPy/SciPy em C para evitar oversubscription
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_MAX_THREADS", "1")

import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime

# Imports DO SEU PIPELINE
import DataSet as ds
import PatternComplexo as pc
import DBScanC as dbc
import AnalisarResultados as ar

# ------------------------------
# 1) Função de trabalho (um cenário)
# ------------------------------
def run_scenario(registros, padroes, itens, repeticoes, intervalo, repeticao_idx):
    """
    Executa UM cenário do pipeline (DataSet -> PatternComplexo -> DBScan -> AnalisarResultados)
    de forma isolada em um processo. Retorna um dicionário com status e tempos.
    """
    try:
        # ------------------------------
        # Identificação de arquivos
        # ------------------------------
        if repeticao_idx < 10:
            m = f"{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_00{repeticao_idx}"
            n = f"{m}.csv"
        elif 10 <= repeticao_idx < 100:
            m = f"{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_0{repeticao_idx}"
            n = f"{m}.csv"
        else:
            m = f"{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}_{repeticao_idx}"
            n = f"{m}.csv"

        # ------------------------------
        # Parâmetros do pipeline
        # ------------------------------
        min_repetitions = min(repeticoes, itens)
        segundos = 0
        minutos = intervalo
        horas = 0
        dias = 0
        tempo = segundos + (minutos * 60) + (horas * 3600) + (dias * 86400)

        pattern_size = itens
        max_time_between_parts = int(tempo / max(1, pattern_size))
        num_linhas = registros
        num_patterns = padroes
        repetitions = repeticoes
        eps = 0.5
        max_items = 30000

        # ------------------------------
        # Execução do pipeline
        # ------------------------------
        t0 = datetime.now()

        # 1) Geração do dataset
        ds.main(m, num_linhas)

        # 2) Inserção de padrões sintéticos (aleatórios)
        pc.generate_random_patterns(n, n, num_patterns, repetitions, pattern_size, max_time_between_parts)

        # 3) Clusterização + Apriori
        dbc.main(m, n, max_items, min_repetitions, tempo, tempo)

        # 4) Análise de resultados
        ar.analyze_clusters(m)
        ar.analyze_data(m, 0, f"Resultado_{registros}_{padroes}_{itens}_{repeticoes}_{intervalo}.txt")

        t1 = datetime.now()

        return {
            "status": "OK",
            "cenario": (registros, padroes, itens, repeticoes, intervalo, repeticao_idx),
            "duracao_s": (t1 - t0).total_seconds()
        }

    except Exception as e:
        return {
            "status": "ERRO",
            "cenario": (registros, padroes, itens, repeticoes, intervalo, repeticao_idx),
            "erro": str(e)
        }

# ------------------------------
# 2) Geração da grade de parâmetros (o que suas “threads” faziam)
# ------------------------------
def gerar_param_grid():
    configs = [
        # Nome é só informativo; aqui devolvemos tuplas diretamente
        dict(registros=[500, 2000, 5000, 10000], padroes=[1,2,3,4,5], itens=[3,4,5,6,7], repeticoes=[3,4,5,6,7], intervalo=[5,10,30,60,120,180]),
        dict(registros=[50000], padroes=[1,2,3,4,5], itens=[3,4,5,6,7], repeticoes=[3,4,5,6,7], intervalo=[5,10,30,60,120,180]),
        dict(registros=[100000], padroes=[1,2,3], itens=[3,4,5,6,7], repeticoes=[3,4,5,6,7], intervalo=[5,10,30,60,120,180]),
        dict(registros=[100000], padroes=[4,5], itens=[3,4,5,6,7], repeticoes=[3,4,5,6,7], intervalo=[5,10,30,60,120,180]),
        dict(registros=[200000], padroes=[1], itens=[3,4,5,6,7], repeticoes=[3,4,5,6,7], intervalo=[5,10,30,60,120,180]),
        dict(registros=[200000], padroes=[2], itens=[3,4,5,6,7], repeticoes=[3,4,5,6,7], intervalo=[5,10,30,60,120,180]),
        dict(registros=[200000], padroes=[3], itens=[3,4,5,6,7], repeticoes=[3,4,5,6,7], intervalo=[5,10,30,60,120,180]),
        dict(registros=[200000], padroes=[4], itens=[3,4,5,6,7], repeticoes=[3,4,5,6,7], intervalo=[5,10,30,60,120,180]),
        dict(registros=[200000], padroes=[5], itens=[3,4,5,6,7], repeticoes=[3,4,5,6,7], intervalo=[5,10,30,60,120,180]),
    ]

    # 10 repetições por cenário (como no seu for k=1..10)
    repeticoes_exec = list(range(1, 11))

    # Explode a grade para tuplas simples
    for cfg in configs:
        for (reg, pad, it, rep, inter) in itertools.product(
            cfg['registros'], cfg['padroes'], cfg['itens'], cfg['repeticoes'], cfg['intervalo']
        ):
            for k in repeticoes_exec:
                yield (reg, pad, it, rep, inter, k)

# ------------------------------
# 3) Runner multiprocessado
# ------------------------------
def main():
    # Máximo: todos os núcleos; pode reduzir se necessário
    workers = os.cpu_count() or 4

    # (Opcional) No Linux: fixar afinidade do processo-mestre
    try:
        os.sched_setaffinity(0, set(range(workers)))
    except Exception:
        pass

    print(f"[INFO] Iniciando pool com {workers} processos...")

    futures = []
    resultados_ok = 0
    resultados_erro = 0

    # Lote de tarefas
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for params in gerar_param_grid():
            futures.append(executor.submit(run_scenario, *params))

        for fut in as_completed(futures):
            res = fut.result()
            if res["status"] == "OK":
                resultados_ok += 1
            else:
                resultados_erro += 1
                cen = res.get("cenario")
                print(f"[ERRO] Cenario {cen} -> {res.get('erro')}")

    print(f"[INFO] Concluído. OK={resultados_ok} | ERROS={resultados_erro}")

if __name__ == "__main__":
    # Em Linux o start method padrão é 'fork' (ok). Se estiver em Windows use:
    # import multiprocessing as mp; mp.set_start_method("spawn", force=True)
    main()
