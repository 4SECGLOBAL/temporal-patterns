import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import warnings
warnings.filterwarnings('ignore')

# Carregar os dados
input_file = '0002.csv'
data = pd.read_csv(input_file)  # Assumindo que o arquivo está no mesmo diretório

# Preparar os dados para clustering (usando origem e destino como features)
X = data[['origem', 'destino']].values

# Arquivo de saída
output_file = input_file.replace('.csv', 'R.txt') 
#output_file = 'resultados_kmeans_apriori.txt'

with open(output_file, 'w') as f:
    for k in range(2, 101):
        f.write(f"\n=== Resultados para K = {k} ===\n")
        
        # Aplicar K-means
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)
        data['cluster'] = clusters
        
        # Processar cada cluster
        for cluster_id in range(k):
            cluster_data = data[data['cluster'] == cluster_id]
            
            # Preparar transações para Apriori (cada linha como uma transação)
            transactions = cluster_data[['origem', 'destino']].astype(str).values.tolist()
            
            # Converter para formato one-hot
            te = TransactionEncoder()
            te_ary = te.fit(transactions).transform(transactions)
            df = pd.DataFrame(te_ary, columns=te.columns_)
            
            # Aplicar Apriori
            try:
                frequent_itemsets = apriori(df, min_support=0.03, use_colnames=True)
                if not frequent_itemsets.empty:
                    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)
                    
                    if not rules.empty:
                        f.write(f"\nCluster {cluster_id} - Regras encontradas:\n")
                        for _, rule in rules.iterrows():
                            antecedents = ', '.join(list(rule['antecedents']))
                            consequents = ', '.join(list(rule['consequents']))
                            f.write(f"{antecedents} => {consequents} (conf: {rule['confidence']:.2f}, sup: {rule['support']:.2f})\n")
                    else:
                        f.write(f"\nCluster {cluster_id} - Nenhuma regra forte encontrada.\n")
                else:
                    f.write(f"\nCluster {cluster_id} - Nenhum itemset frequente encontrado.\n")
            except:
                f.write(f"\nCluster {cluster_id} - Erro ao processar com Apriori.\n")

print("Processo concluído. Resultados salvos em", output_file)