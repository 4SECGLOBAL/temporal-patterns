import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def handle_outliers(data, input_file_path, eps=0.5, min_samples=5, plot=True):
        
    data_clean = data.copy()
    data_clean['timestamp_num'] = pd.to_datetime(data['timestamp']).astype(int) / 10**9
    features = data_clean[['timestamp_num', 'origem', 'destino']]
    
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(features_scaled)
    data_clean['cluster'] = clusters
    
    # Identificar outliers (cluster = -1)
    outliers = data_clean[data_clean['cluster'] == -1]
    clean_data = data_clean[data_clean['cluster'] != -1]
    
    fig = None
    if plot:
        fig = plt.figure(figsize=(12, 8))
        
        ax = fig.add_subplot(111, projection='3d')
        
        ax.scatter(clean_data['origem'], clean_data['destino'], clean_data['timestamp_num'],
                  c=clean_data['cluster'], cmap='viridis', label='Dados Normais')
        
        if not outliers.empty:
            ax.scatter(outliers['origem'], outliers['destino'], outliers['timestamp_num'],
                      c='red', marker='x', s=100, label='Outliers')
        
        ax.set_xlabel('Origem')
        ax.set_ylabel('Destino')
        ax.set_zlabel('Timestamp (numérico)')
        ax.set_title(f'Visualização de Outliers (Total: {len(outliers)}/{len(data)})')
        plt.legend()
        plt.tight_layout()
        
        # Salvar o gráfico como imagem
        output_img = os.path.splitext(input_file_path)[0] + "_outliers.png"
        plt.savefig(output_img)
        print(f"Gráfico de outliers salvo como: {output_img}")
        plt.close()
    
    clean_data = clean_data.drop(columns=['timestamp_num', 'cluster'])
    
    return clean_data, fig

def load_data(file_path):
    """Carrega os dados do arquivo CSV ou Excel"""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Formato de arquivo não suportado. Use CSV ou Excel.")

def preprocess_for_dbscan(data):
    """Prepara os dados para o DBSCAN"""
    data['timestamp_num'] = pd.to_datetime(data['timestamp']).astype(int) / 10**9
    features = data[['timestamp_num', 'origem', 'destino']]
    scaler = StandardScaler()
    return scaler.fit_transform(features)

def apply_dbscan(data_scaled, eps=0.5, min_samples=5):
    """Aplica o algoritmo DBSCAN"""
    return DBSCAN(eps=eps, min_samples=min_samples).fit_predict(data_scaled)

def preprocess_for_apriori(data):
    """Prepara os dados para o Apriori"""
    transactions = data.apply(lambda row: [f"origem_{row['origem']}", f"destino_{row['destino']}"], axis=1).tolist()
    ml_df = pd.DataFrame(transactions)
    ml_df = ml_df.stack().str.get_dummies().groupby(level=0).max()
    return ml_df.astype(bool)

def find_association_rules(transactions, min_support=0.01, min_confidence=0.5):
    """Encontra regras de associação com tratamento de erros"""
    try:
        frequent_itemsets = apriori(transactions, min_support=min_support, use_colnames=True)
        if frequent_itemsets.empty:
            return None
        return association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    except:
        return None

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
    
    output_path = os.path.splitext(input_file_path)[0] + "Apriori.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result_content)
    print(f"Resultados do Apriori salvos em: {output_path}")

def main():
    input_file_path = "0004.csv"  
    
    if not os.path.exists(input_file_path):
        print(f"Erro: Arquivo '{input_file_path}' não encontrado.")
        print("Verifique se:")
        print(f"1. O arquivo existe no diretório: {os.getcwd()}")
        print("2. O nome do arquivo está correto (incluindo a extensão .csv ou .xlsx)")
        return
    
    data = load_data(input_file_path)
    
#     data_scaled = preprocess_for_dbscan(data)
#     data['cluster'] = apply_dbscan(data_scaled)
    
    clean_data, _ = handle_outliers(data, input_file_path, eps=0.5, min_samples=5)
    print(f"Total de registros originais: {len(data)}")
    print(f"Registros após remoção de outliers: {len(clean_data)}")
    print(f"Outliers removidos: {len(data) - len(clean_data)}")
    
    transactions = preprocess_for_apriori(data)
    
    # Ajusta automaticamente o min_support baseado nos dados
    item_counts = transactions.sum()
    auto_min_support = max(0.001, item_counts.max() / len(transactions) * 0.5)
    
    rules = find_association_rules(transactions, min_support=auto_min_support)
    
    save_apriori_results(rules, input_file_path)

if __name__ == "__main__":
    main()