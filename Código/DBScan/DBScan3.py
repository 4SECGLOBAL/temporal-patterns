import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def preprocess_for_dbscan(data):
    data['timestamp_num'] = pd.to_datetime(data['timestamp']).astype(int) / 10**9
    
    features = data[['timestamp_num', 'origem', 'destino']]
    
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    return features_scaled

# DBSCAN
def apply_dbscan(data_scaled, eps=0.5, min_samples=5):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(data_scaled)
    return clusters

# Pré-processamento Apriori
def preprocess_for_apriori(data):
    transactions = data.apply(lambda row: [f"origem_{row['origem']}", f"destino_{row['destino']}"], axis=1).tolist()
    
    ml_df = pd.DataFrame(transactions)
    ml_df = ml_df.stack().str.get_dummies().groupby(level=0).max()
    
    return ml_df

# Apriori
def apply_apriori(transactions, min_support=0.3):
    frequent_itemsets = apriori(transactions, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)
    return frequent_itemsets, rules

def main():
    data = load_data('0001.csv')
    
    print("\n=== Análise com DBSCAN ===")
    data_scaled = preprocess_for_dbscan(data)
    clusters = apply_dbscan(data_scaled)
    
    data['cluster'] = clusters
    print("\nResultados do DBSCAN:")
    print(f"Número de clusters encontrados: {len(set(clusters)) - (1 if -1 in clusters else 0)}")
    print(f"Número de outliers: {list(clusters).count(-1)}")
    print("\nDistribuição dos clusters:")
    print(data['cluster'].value_counts())
    
    # Apriori
    print("\n=== Análise com Apriori ===")
    transactions = preprocess_for_apriori(data)
    
    # Análise exploratória dos dados
    print("\nFrequência de itens individuais:")
    item_counts = transactions.sum().sort_values(ascending=False)
    print(item_counts)
    
    # Ajuste automático do min_support baseado nos dados
    auto_min_support = max(0.001, item_counts.max() / len(transactions) * 0.3)
    print(f"\nUsando min_support automático: {auto_min_support:.4f}")
    
#     frequent_itemsets, rules = apply_apriori(transactions, min_support=auto_min_support)
    frequent_itemsets, rules = apply_apriori(transactions, min_support=0.3)
    
    if not frequent_itemsets.empty:
        print("\nItens frequentes encontrados:")
        print(frequent_itemsets)
        
        if not rules.empty:
            print("\nRegras de associação encontradas:")
            print(rules[['antecedents', 'consequents', 'support', 'confidence']])
        else:
            print("\nNenhuma regra de associação encontrada com o limiar de confiança especificado.")
    else:
        print("\nNenhum padrão frequente encontrado. Tente:")
        print("- Reduzir min_support ainda mais")
        print("- Agrupar origens/destinos em categorias mais amplas")
        print("- Verificar se há dados suficientes para análise")

if __name__ == "__main__":
    main()