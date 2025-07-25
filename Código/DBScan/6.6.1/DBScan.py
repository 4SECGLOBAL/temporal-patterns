import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def handle_outliers(data, input_file_path, eps, min_samples, plot=True):
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
    
    clean_data = clean_data.drop(columns=['timestamp_num', 'cluster'])
    
    return clean_data, figs

def load_data(file_path):
    """Carrega os dados do arquivo CSV ou Excel"""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Formato de arquivo não suportado. Use CSV ou Excel.")
# DBScan
def preprocess_for_dbscan(data):
    """Prepara os dados para o DBSCAN"""
    data['timestamp_num'] = pd.to_datetime(data['timestamp']).astype(int) / 10**9
    features = data[['timestamp_num', 'origem', 'destino']]
    scaler = StandardScaler()
    return scaler.fit_transform(features)

def apply_dbscan(data_scaled, eps=0.5, min_samples=5):
    """Aplica o algoritmo DBSCAN"""
    return DBSCAN(eps=eps, min_samples=min_samples).fit_predict(data_scaled)
# Apriori
def preprocess_for_apriori(data):
    """Prepara os dados para o Apriori"""
    transactions = data.apply(lambda row: [f"origem_{row['origem']}", f"destino_{row['destino']}"], axis=1).tolist()
    ml_df = pd.DataFrame(transactions)
    ml_df = ml_df.stack().str.get_dummies().groupby(level=0).max()
    return ml_df.astype(bool)

def find_association_rules(transactions, min_support, min_confidence = 0.5):
    """Encontra regras de associação com tratamento de erros"""
    try:
        frequent_itemsets = apriori(transactions, min_support=min_support, use_colnames=True)
        if frequent_itemsets.empty:
            return None
        return association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    except:
        return None

def save_apriori_results(rules, input_file_path, clean_data):
    """Salva as regras de associação em um arquivo TXT com timestamps"""
    if rules is None or rules.empty:
        result_content = "Nenhuma regra de associação encontrada com os parâmetros atuais."
    else:
        result_content = "Regras de Associação Encontradas:\n\n"
        rules = rules.sort_values('confidence', ascending=False)
        
        filtered_rules = []
        seen_pairs = set()
        
        for _, row in rules.iterrows():
            antecedents = list(row['antecedents'])
            consequents = list(row['consequents'])
            
            if (all(a.startswith('origem_') for a in antecedents) and 
                all(c.startswith('destino_') for c in consequents)):
                pair = (tuple(antecedents), tuple(consequents))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    filtered_rules.append(row)
        
        # Processar cada regra filtrada
        for row in filtered_rules:

            origem = list(row['antecedents'])[0].replace('origem_', '')
            destino = list(row['consequents'])[0].replace('destino_', '')
            
            timestamps = clean_data[(clean_data['origem'] == int(origem)) & 
                                  (clean_data['destino'] == int(destino))]['timestamp'].tolist()
            
            result_content += f"{set(row['antecedents'])} -> {set(row['consequents'])}\n"
            result_content += f"Confiança: {row['confidence']:.2f}, Suporte: {row['support']:.4f}\n"
            result_content += "Timestamps:\n"
            
            for ts in timestamps:
                result_content += f"  - {ts}\n"
            
            result_content += "\n"
    
    output_path = os.path.splitext(input_file_path)[0] + "Apriori.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result_content)
    print(f"Resultados do Apriori salvos em: {output_path}")

def main(n, repetitions, eps):
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
    
    transactions = preprocess_for_apriori(clean_data)
    
    auto_min_support = max(0.0001, min_repeticao / len(transactions))
    rules = find_association_rules(transactions, min_support=auto_min_support)
    save_apriori_results(rules, input_file_path, clean_data)

if __name__ == "__main__":
    main()

