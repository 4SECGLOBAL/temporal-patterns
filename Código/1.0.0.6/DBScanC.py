import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori, association_rules
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings
from collections import defaultdict
import time


def handle_outliers(k, data, input_file_path, tempo, eps, min_samples, plot=False):
    
#   ============================================================================
                            # PARÂMETROS DE TESTE #
    DEBUG = True
#   ============================================================================  
    
    data_clean = data.copy()
    
    # Tarefa I. Transformação do timestamp em segundos e diferenças temporais 
    try:
        timestamps = pd.to_datetime(data_clean['timestamp'])
        start_time = timestamps.min()
        data_clean['timestamp_num'] = (timestamps - start_time).dt.total_seconds()
    except KeyError:
        raise KeyError("Coluna 'timestamp' não encontrada nos dados")

    data_clean = data_clean.sort_values('timestamp_num')
    
    data_clean['diff_anterior'] = data_clean['timestamp_num'].diff()
    data_clean['diff_posterior'] = data_clean['timestamp_num'].diff(-1).abs()
    
    data_clean['outlier'] = (data_clean['diff_anterior'] > int(0.5*tempo)) & (data_clean['diff_posterior'] > int(0.5*tempo))
    
    # Tarefa II DBSCAN
    data_clean['cluster'] = 0
    current_cluster = 0
    
    for i in range(1, len(data_clean)):
        if not data_clean.iloc[i]['outlier']:
            if data_clean.iloc[i-1]['diff_posterior'] > int(0.5*tempo):
                current_cluster += 1
            data_clean.iloc[i, data_clean.columns.get_loc('cluster')] = current_cluster
    
    # Tarefa III. Filtrar dados
    cluster_sizes = data_clean['cluster'].value_counts()
    valid_clusters = cluster_sizes[cluster_sizes >= min_samples].index
    
    data_clean['valid_cluster'] = data_clean['cluster'].isin(valid_clusters)
    
    clean_data = data_clean[
        ~data_clean['outlier'] &
        data_clean['cluster'].isin(valid_clusters)
    ].copy()
    
    outliers = data_clean[
        data_clean['outlier'] |
        ~data_clean['cluster'].isin(valid_clusters)
    ]
    
    # Tarefa IV. Visualização
    figs = []
    if plot:
        
        # Figura 1: Com outliers
        fig1 = plt.figure(figsize=(12, 8))
        ax1 = fig1.add_subplot(111, projection='3d')
        
        for cluster_id in np.unique(data_clean['cluster']):
            cluster_data = data_clean[data_clean['cluster'] == cluster_id]
            ax1.scatter(cluster_data['origem'], cluster_data['destino'], cluster_data['timestamp_num'],
                      label=f'Cluster {cluster_id}', alpha=0.7)

        if not outliers.empty:
            ax1.scatter(outliers['origem'], outliers['destino'], outliers['timestamp_num'],
                      c='red', marker='x', s=100, label='Outliers')
        
        ax1.set_title(f'Dados com Outliers (Total: {len(outliers)}/{len(data_clean)})')
        ax1.legend()
        
        # Figura 2:  Dados limpos e clusters
        fig2 = plt.figure(figsize=(12, 20))
        ax2 = fig2.add_subplot(111, projection='3d')
        
        for cluster_id in np.unique(data_clean['cluster']):
            cluster_data = data_clean[data_clean['cluster'] == cluster_id]
            ax2.scatter(cluster_data['origem'], cluster_data['destino'], cluster_data['timestamp_num'],
                      label=f'Cluster {cluster_id}', alpha=0.4)
        
        ax2.set_title('Dados Limpos Clusterizados')
        ax2.legend(loc='upper left')
        
        # Salvar figuras
        if input_file_path:
            base_name = os.path.splitext(input_file_path)[0]
            fig1.savefig(f"{base_name}Outliers.png", dpi=300)
            fig2.savefig(f"{base_name}Clean.png", dpi=300)
            print(f"Gráficos salvos em:\n- {base_name}Outliers.png\n- {base_name}Clean.png")
        
        plt.close('all')
        figs.extend([fig1, fig2])

        clean_data = clean_data.drop(columns=[
            'timestamp_num', 'diff_anterior', 'diff_posterior', 
            'outlier', 'cluster'
         ])
        
        
    if DEBUG:
        data_clean.to_csv(f'ResLOG_{k}.txt', sep='\t', index=True)
        
    return clean_data, figs

def load_data(file_path):
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Formato de arquivo não suportado. Use CSV ou Excel.")

def preprocess_for_dbscan(data):

    data['timestamp_num'] = pd.to_datetime(data['timestamp']).astype(int) / 10**9
    features = data[['timestamp_num', 'origem', 'destino']]
    scaler = StandardScaler()
    return scaler.fit_transform(features)

def apriori_particionado(data, max_items, min_support, min_confidence):
    
    from collections import defaultdict
    import itertools
    from datetime import datetime

    if data.empty or len(data) == 0:
        return pd.DataFrame()


    item_counts = defaultdict(int)
    transaction_list = []

    # Tarefa I: itens frequentes
    for _, row in data.iterrows():
        origem = f"origem_{row['origem']}"
        destino = f"destino_{row['destino']}"
        transaction = {origem, destino}
        
        
        # NO MOMENTO DE DEFINIR OS ITENS, POSSO PEGAR ESSE transaction
        # transactionA = {origem, destino) e transactionB = (destino, origem) -> são a mesma coisa
        
        for item in transaction:
            item_counts[item] += 1
        transaction_list.append(transaction)
    total_transactions = len(transaction_list)
    min_count = min_support * total_transactions

    frequent_items = {item for item, count in item_counts.items() if count >= min_count}
    
    if len(frequent_items) > max_items:
        sorted_items = sorted(item_counts.items(), key=lambda x: -x[1])
        frequent_items = {item for item, _ in sorted_items[:max_items]}

    # Tarefa II: pares válidos
    pair_counts = defaultdict(int)
    
    for transaction in transaction_list:
        freq_items = [item for item in transaction if item in frequent_items]
        
        for pair in itertools.combinations(freq_items, 2):
            ordered_pair = tuple(sorted(pair))
            pair_counts[ordered_pair] += 1

    itemsets = []
    for pair, count in pair_counts.items():
        support = count / total_transactions
        if support >= min_support:
            itemsets.append({
                'support': support,
                'itemsets': frozenset(pair)
            })

    if not itemsets:
        return pd.DataFrame()

    frequent_itemsets = pd.DataFrame(itemsets)

    # Tarefa III: Gerar regras de associação
    rules = []
    for _, row in frequent_itemsets.iterrows():
        itemset = list(row['itemsets'])
        if len(itemset) == 2:
            origem = next(item for item in itemset if item.startswith('origem_'))
            destino = next(item for item in itemset if item.startswith('destino_'))
            
            support = row['support']
            confidence = pair_counts[tuple(sorted([origem, destino]))] / item_counts[origem]
            
            if confidence >= min_confidence:
                rules.append({
                    'antecedents': {origem},
                    'consequents': {destino},
                    'support': support,
                    'confidence': confidence
                })

    if not rules:
        return pd.DataFrame()

    return pd.DataFrame(rules).sort_values('confidence', ascending=False)

def group_patterns_by_time(rules, clean_data, eps):
    if rules.empty:
        return []

    # Tarefa I. Extrair timestamps para cada regra
    rule_timestamps = []
    for idx, row in rules.iterrows():
        origem = list(row['antecedents'])[0].replace('origem_', '')
        destino = list(row['consequents'])[0].replace('destino_', '')
        timestamps = clean_data[(clean_data['origem'] == int(origem)) & 
                             (clean_data['destino'] == int(destino))]['timestamp'].tolist()
        
        rule_info = {
            'rule_idx': idx,  # Índice único da regra no DataFrame original
            'rule': row,
            'origem': origem,
            'destino': destino,
            'timestamps': [pd.to_datetime(ts) for ts in timestamps]
        }
        rule_timestamps.append(rule_info)

    # Tarefa II. Agrupar todas as repetições de cada padrão
    pattern_groups = {}
    for rt in rule_timestamps:
        key = (rt['origem'], rt['destino'])
        if key not in pattern_groups:
            pattern_groups[key] = []
        pattern_groups[key].append(rt)

    def is_rule_in_group(rule, group):
        return any(r['rule_idx'] == rule['rule_idx'] for r in group)

    groups = []
    used_indices = set()

    for i, rt1 in enumerate(rule_timestamps):
        if i in used_indices:
            continue

        # Tarefa III.1. Iniciar novo grupo com a regra atual
        group = [rt1]
        used_indices.add(i)
        current_pattern = (rt1['origem'], rt1['destino'])
        
        # Tarefa III.2. Adicionar repetições do mesmo padrão
        for repeat in pattern_groups.get(current_pattern, []):
            if not is_rule_in_group(repeat, group):
                group.append(repeat)
                used_indices.add(rule_timestamps.index(repeat))

        for rt2 in rule_timestamps:
            if is_rule_in_group(rt2, group) or (rt2['origem'], rt2['destino']) == current_pattern:
                continue

            # Tarefa III.3. Verificação temporal
            for rt_group in group:
                for ts1 in rt_group['timestamps']:
                    for ts2 in rt2['timestamps']:
                        if abs((ts1 - ts2).total_seconds()) <= eps:
                            if not is_rule_in_group(rt2, group):
                                group.append(rt2)
                                used_indices.add(rule_timestamps.index(rt2))

                                new_pattern = (rt2['origem'], rt2['destino'])
                                for repeat in pattern_groups.get(new_pattern, []):
                                    if not is_rule_in_group(repeat, group):
                                        group.append(repeat)
                                        used_indices.add(rule_timestamps.index(repeat))
                            break
                    else:
                        continue
                    break

        groups.append(group)
    return groups

def save_apriori_results(rules, input_file_path, clean_data, tempo, min_repeticao):
    if rules is None or rules.empty:
        result_content = "Nenhuma regra de associação encontrada com os parâmetros atuais."
    else:
        result_content = "Grupos de padrões encontrados:"
        rules = rules.sort_values('confidence', ascending=False)
        
        # Tarefa I. Filtrar e preparação das regras
        filtered_rules = []
        filteredCopy = []
        seen_pairs = set()
        
        for _, row in rules.iterrows():
            rowCopy=row.copy()
            primeiro = 0
            segundo = 0
            antecedents = list(row['antecedents'])
            consequents = list(row['consequents'])
            
            if (all(a.startswith('origem_') for a in antecedents) and 
               (all(c.startswith('destino_') for c in consequents))):
                pair = (tuple(antecedents), tuple(consequents))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    # Tarefa I.1. Adiciona o valor do cluster como base
                    origem = int(antecedents[0].replace('origem_', ''))
                    destino = int(consequents[0].replace('destino_', ''))
                    
                    for c in enumerate (clean_data[clean_data['destino'] == destino]['cluster']):
                        for d in enumerate (clean_data[clean_data['origem'] == origem]['cluster']):
                            if c[1] == d[1]:
                                if segundo == 1:
                                    segundo == 0
                                    rowCopy['cluster'] = c[1]
                                    filteredCopy.append(rowCopy)
                                if primeiro == 0:
                                    primeiro = 1
                                    row['cluster'] = c[1]
                                    filtered_rules.append(row)
                                    segundo = 1

        # Tarefa I.2. Verificação da melhor captura de padrão
        if len(filteredCopy) != len(filtered_rules):
            if len(filteredCopy) == len(rules):
                filtered_rules = filteredCopy
        
        # Tarefa II. Agrupamento por tempo no cluster
        cluster_groups = defaultdict(list)
        for rule in filtered_rules:
            cluster_groups[rule['cluster']].append(rule)
            
        for cluster_id, cluster_rules in cluster_groups.items():
            result_content += f"\n\n=== Cluster {cluster_id} ===\n"

            groups = group_patterns_by_time(pd.DataFrame(cluster_rules), clean_data, tempo)

            if not groups:
                result_content += "Nenhuma sequência significativa encontrada neste cluster.\n"
                continue
                
            for group_num, group in enumerate(groups, 1):
                if len(group) < 2:
                    continue
                    
                group_content = f"\nSequência {group_num}:\n"
                for rt in group:
                    group_content += f"  {set(rt['rule']['antecedents'])} -> {set(rt['rule']['consequents'])}\n"
                    group_content += f"  Confiança: {rt['rule']['confidence']:.3f}, Suporte: {rt['rule']['support']:.6f}\n"
                
                # Tarefa III. Obter os timestamps das regras
                timestamps = []
                for rt in group:
                    origem = int(list(rt['rule']['antecedents'])[0].replace('origem_', ''))
                    destino = int(list(rt['rule']['consequents'])[0].replace('destino_', ''))
                    ts_data = clean_data[(clean_data['origem'] == origem) & 
                                        (clean_data['destino'] == destino)][['timestamp', 'cluster']]
                    for _, row in ts_data.iterrows():
                        timestamps.append({
                            'rule': rt,
                            'timestamp': row['timestamp'],
                            'cluster': row['cluster']
                        })
                
                timestamps.sort(key=lambda x: pd.to_datetime(x['timestamp']))
                # Tarefa IV. Identifica apenas as sequências completas
                sequences = []
                current_sequence = []
                completed_sequences = set()  # Para controlar sequências já completas

                for entry in timestamps:
                    if not current_sequence:
                        current_sequence.append(entry)
                    else:
                        # Verifica se o padrão atual já completou uma sequência
                        current_pattern = (entry['rule']['origem'], entry['rule']['destino'])
                        
                        if current_pattern in completed_sequences:
                            # Se já completou, inicia uma nova sequência
                            if is_complete_sequence(current_sequence, group):
                                sequences.append(current_sequence)
                            current_sequence = [entry]
                            completed_sequences = set()  # Reseta para a nova sequência
                        else:
                            # Lógica normal de agrupamento por tempo
                            time_diff = (pd.to_datetime(entry['timestamp']) - 
                                       pd.to_datetime(current_sequence[-1]['timestamp'])).total_seconds()
                            
                            if time_diff <= tempo:
                                current_sequence.append(entry)
                                # Verifica se completou todos os padrões
                                if is_complete_sequence(current_sequence, group):
                                    completed_sequences.update(
                                        (e['rule']['origem'], e['rule']['destino']) 
                                        for e in current_sequence
                                    )
                            else:
                                if is_complete_sequence(current_sequence, group):
                                    sequences.append(current_sequence)
                                current_sequence = [entry]
                                completed_sequences = set()

                # Verifica a última sequência
                if current_sequence and is_complete_sequence(current_sequence, group):
                    sequences.append(current_sequence)
    
                # Tarefa V. Seleciona as que atendem ao mínimo de repetições
                if len(sequences) >= min_repeticao:
                    result_content += group_content
                    result_content += f"\nRepetições completas: {len(sequences)}\n"
                    
                    if sequences:
                        result_content += "\nHorários:\n"
                        for seq_num, seq in enumerate(sequences, 1):
                            result_content += f"\nRepetição {seq_num}:\n"
                            for entry in seq:
                                rt = entry['rule']
                                result_content += f"{set(rt['rule']['antecedents'])} -> {set(rt['rule']['consequents'])}\n"
                                result_content += f"    - {entry['timestamp']}\n"
    
    # Salva o resultado
    output_path = os.path.splitext(input_file_path)[0] + "Apriori.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result_content)
#     print(f"Resultados do Apriori salvos em: {output_path}")

def is_complete_sequence(sequence, group):

    required_patterns = set()
    
    # Passo 1: Extrai padrões do grupo (já limpos, pois group usa 'origem'/'destino' diretamente)
    for rt in group:
        origem = str(rt['origem'])
        destino = str(rt['destino'])
        required_patterns.add((origem, destino))
    
    # Passo 2: Extrai padrões da sequência
    found_patterns = set()
    for entry in sequence:
        origem = str(entry['rule']['origem'])
        destino = str(entry['rule']['destino'])
        found_patterns.add((origem, destino))
        
    return required_patterns.issubset(found_patterns)
    

def main(k, n, max_items, repetitions, eps, tempo, confianca):
    input_file_path = n
    min_repeticao = repetitions
    
    if not os.path.exists(input_file_path):
        print(f"Erro: Arquivo '{input_file_path}' não encontrado.")
        print("Verifique se:")
        print(f"1. O arquivo existe no diretório: {os.getcwd()}")
        print("2. O nome do arquivo está correto (incluindo a extensão .csv ou .xlsx)")
        return
    
    data = load_data(input_file_path)
    inicioDB = time.time()
    clean_data, _ = handle_outliers(k, data, input_file_path, tempo, eps, min_repeticao)
    fimDB = time.time()
#     print(f"Tempo de processamento DBScan {n}: {fimDB - inicioDB:.6f} segundos")
    
    
#     print(f"Total de registros originais: {len(data)}")
#     print(f"Registros após remoção de outliers: {len(clean_data)}")
#     print(f"Outliers removidos: {len(data) - len(clean_data)}")
    
    auto_min_support = 0.9*(min_repeticao / len(clean_data))
    # MD20-006/MD20-009 -> adicionado uma folga de 10% ao suporte
    inicioAP = time.time()
    rules = apriori_particionado(
        clean_data,
        max_items,
        min_support=auto_min_support,
        min_confidence=confianca
    )
    fimAP = time.time()
#     print(f"Tempo de processamento Apriori {n}: {fimAP - inicioAP:.6f} segundos")
    save_apriori_results(rules, input_file_path, clean_data, tempo, min_repeticao)
    
    out_file = "Tempo.txt"
    with open(out_file, 'a', encoding='utf-8') as out_file:
        out_file.write(f"\n=== Análise detalhada para tempo de processamento ===\n")
        out_file.write(f"Tempo de processamento Apriori {n}: {fimAP - inicioAP:.6f} segundos\n")
        out_file.write(f"Tempo de processamento DBScan {n}: {fimDB - inicioDB:.6f} segundos\n")
    
if __name__ == "__main__":
    main()
