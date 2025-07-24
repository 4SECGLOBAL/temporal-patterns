import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori, association_rules
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings

def handle_outliers(data, input_file_path, eps, min_samples, plot=True):
    data_clean = data.copy()
    
    # Normalização I: segundos
    timestamps = pd.to_datetime(data['timestamp'])
    start_time = timestamps.min()  # Tempo de referência (será 0)
    data_clean['timestamp_num'] = (timestamps - start_time).dt.total_seconds()
    
    features = data_clean[['timestamp_num', 'origem', 'destino']]
    n_samples = len(features)

    # Normalização II
    scaler = StandardScaler()
    features_scaled = features.copy()
    features_scaled[['origem', 'destino']] = scaler.fit_transform(features[['origem', 'destino']])
    
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(features_scaled)
    
    data_clean['cluster'] = clusters
    
    # Identificar outliers (cluster = -1)
    outliers = data_clean[data_clean['cluster'] == -1]
    clean_data = data_clean[data_clean['cluster'] != -1]
    
    figs = []
    if plot:
        # Figura 1: Com outliers (original)
        fig1 = plt.figure(figsize=(12, 8))
        ax1 = fig1.add_subplot(111, projection='3d')
        
        ax1.scatter(clean_data['origem'], clean_data['destino'], clean_data['timestamp_num'],
                  c=clean_data['cluster'], cmap='viridis', label='Dados Normais')
        
        if not outliers.empty:
            ax1.scatter(outliers['origem'], outliers['destino'], outliers['timestamp_num'],
                      c='red', marker='x', s=100, label='Outliers')
        
        ax1.set_xlabel('Origem')
        ax1.set_ylabel('Destino')
        ax1.set_zlabel('Timestamp (numérico)')
        ax1.set_title(f'Visualização com Outliers (Total: {len(outliers)}/{len(data)})')
        plt.legend()
        plt.tight_layout()
        
        output_img1 = os.path.splitext(input_file_path)[0] + "_outliers.png"
        plt.savefig(output_img1)
        print(f"Gráfico com outliers salvo como: {output_img1}")
        plt.close(fig1)
        figs.append(fig1)
        
        # Figura 2: Sem outliers (apenas dados normais)
        fig2 = plt.figure(figsize=(12, 8))
        ax2 = fig2.add_subplot(111, projection='3d')
        
        ax2.scatter(clean_data['origem'], clean_data['destino'], clean_data['timestamp_num'],
                  c=clean_data['cluster'], cmap='viridis')
        
        ax2.set_xlabel('Origem')
        ax2.set_ylabel('Destino')
        ax2.set_zlabel('Timestamp (numérico)')
        ax2.set_title('Visualização sem Outliers')
        plt.tight_layout()

        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_img2 = os.path.splitext(input_file_path)[0] + "_clean.png"
        plt.savefig(output_img2)
        print(f"Gráfico sem outliers salvo como: {output_img2}")
        plt.close(fig2)
        figs.append(fig2)
    
    clean_data = clean_data.drop(columns=['timestamp_num', 'cluster'])
    
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

def apply_dbscan(data_scaled, eps=0.5, min_samples=5):

    return DBSCAN(eps=eps, min_samples=min_samples).fit_predict(data_scaled)

def apriori_with_chunks(data, max_items, min_support, min_confidence):
    
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

    # Extrair timestamps para cada regra
    rule_timestamps = []
    for _, row in rules.iterrows():
        origem = list(row['antecedents'])[0].replace('origem_', '')
        destino = list(row['consequents'])[0].replace('destino_', '')
        timestamps = clean_data[(clean_data['origem'] == int(origem)) & 
                              (clean_data['destino'] == int(destino))]['timestamp'].tolist()
        rule_timestamps.append({
            'rule': row,
            'timestamps': [pd.to_datetime(ts) for ts in timestamps]
        })

    # Agrupar regras com timestamps próximos
    groups = []
    used_indices = set()

    for i, rt1 in enumerate(rule_timestamps):
        if i in used_indices:
            continue

        group = [rt1]
        used_indices.add(i)

        for j, rt2 in enumerate(rule_timestamps[i+1:], start=i+1):
            if j in used_indices:
                continue

            for ts1 in rt1['timestamps']:
                for ts2 in rt2['timestamps']:
                    if abs((ts1 - ts2).total_seconds()) <= eps:
                        group.append(rt2)
                        used_indices.add(j)
                        break
                else:
                    continue
                break

        groups.append(group)

    return groups

def save_apriori_results(rules, input_file_path, clean_data, eps, min_repeticao):
    if rules is None or rules.empty:
        result_content = "Nenhuma regra de associação encontrada com os parâmetros atuais."
    else:
        result_content = ""
        rules = rules.sort_values('confidence', ascending=False)
        
        filtered_rules = []
        seen_pairs = set()
        
        # Processar Regras
        for _, row in rules.iterrows():
            antecedents = list(row['antecedents'])
            consequents = list(row['consequents'])
            
            if (all(a.startswith('origem_') for a in antecedents) and 
                all(c.startswith('destino_') for c in consequents)):
                pair = (tuple(antecedents), tuple(consequents))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    filtered_rules.append(row)
        
        # Tarefas: grupos temporais determinados por eps
        groups = group_patterns_by_time(pd.DataFrame(filtered_rules), clean_data, eps)
        if groups:
            result_content += "\nPadrões em sequência (eps = {} segundos):\n\n".format(eps)
            
            filtered_groups = [group for group in groups if len(group) >= 2]
            
            # Tarefa I: filtragem e amostragem dos grupos
            for i, group in enumerate(filtered_groups, start=1):
                n_items = len(group)
                group_rules_content = f"Sequência {i}:\n"
                
                for rt in group:
                    group_rules_content += f"  {set(rt['rule']['antecedents'])} -> {set(rt['rule']['consequents'])}\n"
                    group_rules_content += f"  Confiança: {rt['rule']['confidence']:.3f}, Suporte: {rt['rule']['support']:.6f}\n"
                
                all_timestamps = []
                for rt in group:
                    origem = list(rt['rule']['antecedents'])[0].replace('origem_', '')
                    destino = list(rt['rule']['consequents'])[0].replace('destino_', '')
                    timestamps = clean_data[(clean_data['origem'] == int(origem)) & 
                                          (clean_data['destino'] == int(destino))]['timestamp'].tolist()
                    all_timestamps.extend([(rt, ts) for ts in timestamps])
                
                all_timestamps.sort(key=lambda x: pd.to_datetime(x[1]))
                
                # Tarefa II: Agrupamento (se eps <= tempo)
                group_repetitions = []
                current_sequence = []
                used_timestamps = set()
                
                for rt, ts in all_timestamps:
                    ts_dt = pd.to_datetime(ts)
                    if not current_sequence:
                        current_sequence.append((rt, ts_dt))
                        used_timestamps.add(ts)
                    else:
                        first_ts = current_sequence[0][1]
                        if abs((ts_dt - first_ts).total_seconds()) <= eps:
                            current_sequence.append((rt, ts_dt))
                            used_timestamps.add(ts)
                        else:
                            unique_items = {tuple(rt['rule']['antecedents']) for rt, _ in current_sequence}
                            if len(unique_items) == n_items:
                                group_repetitions.append(current_sequence)
                            current_sequence = [(rt, ts_dt)]
                            used_timestamps = {ts}
                
                # Tarefa III: Verificação da sequência
                if current_sequence:
                    unique_items = {tuple(rt['rule']['antecedents']) for rt, _ in current_sequence}
                    if len(unique_items) == n_items:
                        group_repetitions.append(current_sequence)
                
                # Tarefa IV: Contar repetições completas
                repetition_count = len(group_repetitions)
                
                if repetition_count >= min_repeticao:
                    result_content += group_rules_content
                    result_content += f"\nRepetições completas: {repetition_count}\n"
                    
                    if repetition_count > 0:
                        result_content += "\nHorários:\n\n"
                        for seq in group_repetitions:
                            for rt, ts in seq:
                                result_content += f"{set(rt['rule']['antecedents'])} -> {set(rt['rule']['consequents'])}\n"
                                result_content += f"    - {ts}\n"
                            result_content += "\n"
                    else:
                        result_content += "\nTimestamps: Nenhuma repetição completa encontrada.\n\n"
    
    output_path = os.path.splitext(input_file_path)[0] + "Apriori.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result_content)
    print(f"Resultados do Apriori salvos em: {output_path}")
    

def main(n, max_items, repetitions, eps):
    input_file_path = n
    min_repeticao = repetitions
    
    if not os.path.exists(input_file_path):
        print(f"Erro: Arquivo '{input_file_path}' não encontrado.")
        print("Verifique se:")
        print(f"1. O arquivo existe no diretório: {os.getcwd()}")
        print("2. O nome do arquivo está correto (incluindo a extensão .csv ou .xlsx)")
        return
    
    data = load_data(input_file_path)
    clean_data, _ = handle_outliers(data, input_file_path, eps, min_repeticao)
    
    print(f"Total de registros originais: {len(data)}")
    print(f"Registros após remoção de outliers: {len(clean_data)}")
    print(f"Outliers removidos: {len(data) - len(clean_data)}")
    
#     auto_min_support = max(0.0001, min_repeticao / len(clean_data))
    auto_min_support = min_repeticao / len(clean_data)
    rules = apriori_with_chunks(
        clean_data,
        max_items,
        min_support=auto_min_support,
        min_confidence=0.2
    )
    
    save_apriori_results(rules, input_file_path, clean_data, eps, min_repeticao)

if __name__ == "__main__":
    main()