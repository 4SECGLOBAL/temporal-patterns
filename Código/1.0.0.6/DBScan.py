import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
from collections import defaultdict
import itertools

def handle_outliers(k, data, input_file_path, eps, min_samples, plot=False):
    data_clean = data.copy()
    
    # Converter timestamp para datetime e normalizar para segundos relativos
    timestamps = pd.to_datetime(data['timestamp'])
    start_time = timestamps.min()  # Tempo de referência (será 0)
    data_clean['timestamp_num'] = (timestamps - start_time).dt.total_seconds()
    
    features = data_clean[['timestamp_num', 'origem', 'destino']]
    
    # Ajuste automático de min_samples para datasets grandes
    n_samples = len(features)
    if min_samples is None:
        min_samples = min(30, max(5, int(np.log(n_samples) * 5)))
    
    # Normalização (apenas para origem e destino, mantendo timestamp_rel em segundos)
    scaler = StandardScaler()
    features_scaled = features.copy()
    features_scaled[['origem', 'destino']] = scaler.fit_transform(features[['origem', 'destino']])
    
    # Se eps não for fornecido, calcular automaticamente
    if eps is None:
        from sklearn.neighbors import NearestNeighbors
        neigh = NearestNeighbors(n_neighbors=min_samples)
        nbrs = neigh.fit(features_scaled)
        distances, _ = nbrs.kneighbors(features_scaled)
        eps = np.percentile(distances[:, -1], 90)
    else:
        # Ajustar o eps para a escala das outras features
        # Manter o valor original para o tempo (já está em segundos)
        eps_time = eps
        eps_other = eps / scaler.scale_.mean()  # Aproximação para origem/destino
        eps = np.sqrt(eps_time**2 + eps_other**2)  # Distância euclidiana combinada
    
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
        
        # Salvar a primeira figura
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
        
        # Salvar a segunda figura
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_img2 = os.path.splitext(input_file_path)[0] + "_clean.png"
        plt.savefig(output_img2)
        print(f"Gráfico sem outliers salvo como: {output_img2}")
        plt.close(fig2)
        figs.append(fig2)
    
    # Salvar arquivo com resultados do DBSCAN
    data_clean.to_csv(f'ResLOG_{k}_Classico.txt', sep='\t', index=True)
    
    # Retornar dados limpos SEM as colunas temporárias para o Apriori
    clean_data_for_apriori = clean_data.drop(columns=['timestamp_num', 'cluster'])
    
    return clean_data_for_apriori, figs

def load_data(file_path):
    """Carrega os dados do arquivo CSV ou Excel"""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Formato de arquivo não suportado. Use CSV ou Excel.")

def apriori_particionado(data, max_items, min_support, min_confidence):
    """Versão otimizada do Apriori para evitar estouro de memória"""
    
    if data.empty or len(data) == 0:
        print("Dados vazios para o Apriori")
        return pd.DataFrame()

    item_counts = defaultdict(int)
    transaction_list = []

    # Tarefa I: itens frequentes
    print("Contando itens frequentes...")
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
    
    # Limitar número máximo de itens para evitar explosão combinatória
    if len(frequent_items) > max_items:
        sorted_items = sorted(item_counts.items(), key=lambda x: -x[1])
        frequent_items = {item for item, _ in sorted_items[:max_items]}
        print(f"Limitado a {max_items} itens mais frequentes")

    print(f"Encontrados {len(frequent_items)} itens frequentes")

    # Tarefa II: pares válidos
    print("Gerando pares frequentes...")
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
        print("Nenhum itemset frequente encontrado")
        return pd.DataFrame()

    frequent_itemsets = pd.DataFrame(itemsets)
    print(f"Encontrados {len(frequent_itemsets)} pares frequentes")

    # Tarefa III: Gerar regras de associação
    print("Gerando regras de associação...")
    rules = []
    for _, row in frequent_itemsets.iterrows():
        itemset = list(row['itemsets'])
        if len(itemset) == 2:
            # Encontrar origem e destino no par
            origem = next((item for item in itemset if item.startswith('origem_')), None)
            destino = next((item for item in itemset if item.startswith('destino_')), None)
            
            if origem and destino:
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
        print("Nenhuma regra de associação encontrada")
        return pd.DataFrame()

    result_df = pd.DataFrame(rules).sort_values('confidence', ascending=False)
    print(f"Geradas {len(result_df)} regras de associação")
    
    return result_df

def save_apriori_results(rules, input_file_path):
    """Salva apenas as regras de associação em um arquivo TXT"""
    if rules is None or rules.empty:
        result_content = "Nenhuma regra de associação encontrada com os parâmetros atuais."
    else:
        result_content = "Regras de Associação Encontradas:\n\n"
        rules = rules.sort_values('confidence', ascending=False)
        for _, row in rules.iterrows():
            result_content += (f"{set(row['antecedents'])} -> {set(row['consequents'])} "
                            f"(Confiança: {row['confidence']:.2f}, Suporte: {row['support']:.4f})\n")
    
    output_path = os.path.splitext(input_file_path)[0] + "_Apriori.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result_content)
    print(f"Resultados do Apriori salvos em: {output_path}")

def main(n, repetitions, eps, max_items, min_confidence):
    input_file_path = n
    min_repeticao = repetitions
    
    if not os.path.exists(input_file_path):
        print(f"Erro: Arquivo '{input_file_path}' não encontrado.")
        print("Verifique se:")
        print(f"1. O arquivo existe no diretório: {os.getcwd()}")
        print("2. O nome do arquivo está correto (incluindo a extensão .csv ou .xlsx)")
        return
    
    # Carregar dados
    data = load_data(input_file_path)
    print(f"Total de registros originais: {len(data)}")
    
    # Aplicar DBSCAN
    inicioDB = time.time()
    clean_data, _ = handle_outliers(n, data, input_file_path, eps, min_repeticao)
    fimDB = time.time()
    
    print(f"Registros após remoção de outliers: {len(clean_data)}")
    print(f"Outliers removidos: {len(data) - len(clean_data)}")
    
    # Aplicar Apriori
    auto_min_support = 0.9*(min_repeticao / len(clean_data))
    inicioAP = time.time()
    
    if len(clean_data) > 0:
        rules = apriori_particionado(
            clean_data, 
            max_items=max_items,
            min_support=auto_min_support, 
            min_confidence=min_confidence
        )
        save_apriori_results(rules, input_file_path)
        print(rules)
    else:
        print("Nenhum dado disponível para o Apriori após a limpeza")
    
    fimAP = time.time()
    
    # Salvar tempos de processamento
#     out_file = "Tempo.txt"
#     with open(out_file, 'a', encoding='utf-8') as out_file:
#         out_file.write(f"\n=== Análise detalhada para tempo de processamento ===\n")
#         out_file.write(f"Tempo de processamento Apriori {n}: {fimAP - inicioAP:.6f} segundos\n")
#         out_file.write(f"Tempo de processamento DBScan {n}: {fimDB - inicioDB:.6f} segundos\n")
#         out_file.write(f"Parâmetros Apriori - max_items: {max_items}, min_support: {min_support}, min_confidence: {min_confidence}\n")

if __name__ == "__main__":
    main()