import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler
from math import sqrt
from tqdm import tqdm
import matplotlib
matplotlib.use('TkAgg')

def optimized_clustering(file_path, fig_path):
    # Carregar e preparar dados
    data = pd.read_csv(file_path)
    metadata = 'timestamp'
    origem = 'origem'
    destino = 'destino'
    
    # Converter timestamp e ordenar
    data[metadata] = pd.to_datetime(data[metadata])
    data = data.sort_values(metadata).reset_index(drop=True)
    
    # Engenharia de features
    data['timestamp_seconds'] = (data[metadata] - data[metadata].min()).dt.total_seconds()
    contagem = data.groupby([origem, destino]).size()
    data['frequencia_rota'] = data.apply(lambda x: contagem[(x[origem], x[destino])], axis=1)
    
    # Seleção e normalização de features
    features = ['timestamp_seconds', 'frequencia_rota']
    X = data[features].values
    X_scaled = StandardScaler().fit_transform(X)
    
    # Determinação dinâmica do número de clusters
    n_samples = len(X_scaled)
    kmin = 2
    kmax = min(50, int(sqrt(n_samples)))  # Limite superior adaptativo
    
    # Algoritmo adaptativo para diferentes tamanhos de dataset
    if n_samples > 10000:  # Dataset grande
        print("Usando Davies-Bouldin para dataset grande...")
        scores = []
        for k in tqdm(range(kmin, kmax+1), desc="Avaliando clusters"):
            kmeans = MiniBatchKMeans(n_clusters=k, batch_size=1024, random_state=42).fit(X_scaled)
            scores.append(davies_bouldin_score(X_scaled, kmeans.labels_))
        optimal_k = np.argmin(scores) + kmin
    else:  # Dataset pequeno/médio
        print("Usando Silhouette para dataset pequeno/médio...")
        sil_scores = []
        for k in tqdm(range(kmin, kmax+1), desc="Avaliando clusters"):
            kmeans = MiniBatchKMeans(n_clusters=k, random_state=42).fit(X_scaled)
            sil_scores.append(silhouette_score(X_scaled, kmeans.labels_))
        optimal_k = np.argmax(sil_scores) + kmin
    
    # Clusterização final
    final_kmeans = MiniBatchKMeans(n_clusters=optimal_k, batch_size=1024, random_state=42)
    data['Cluster'] = final_kmeans.fit_predict(X_scaled)
    
    # Visualização adaptativa
    plt.figure(figsize=(12, 6))
    
    if n_samples > 5000:  # Amostragem para datasets grandes
        sample = data.sample(n=5000, random_state=42)
        plt.scatter(sample['timestamp_seconds'], sample['frequencia_rota'], 
                   c=sample['Cluster'], cmap='viridis', alpha=0.6)
    else:
        plt.scatter(data['timestamp_seconds'], data['frequencia_rota'], 
                   c=data['Cluster'], cmap='viridis')
    
    plt.xlabel('Tempo (segundos desde o início)')
    plt.ylabel('Frequência da Rota')
    plt.title(f'Clusterização Ótima (k={optimal_k})')
    plt.colorbar(label='Cluster')
    plt.savefig(fig_path)
    plt.close()
    
    # Análise dos clusters
    cluster_stats = data.groupby('Cluster')[features].agg(['mean', 'std', 'count'])
    print("\nEstatísticas por Cluster:")
    print(cluster_stats)
    
    return data, optimal_k

# Uso
file = '0001.csv'
fig = '0001_optimized.png'
resultados, k_ideal = optimized_clustering(file, fig)
print(f"\nNúmero ideal de clusters determinado: {k_ideal}")