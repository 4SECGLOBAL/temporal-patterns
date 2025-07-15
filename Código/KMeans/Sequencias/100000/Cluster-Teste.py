import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from math import sqrt
from tqdm import tqdm
import matplotlib
matplotlib.use('TkAgg')

file = '0001.csv'
fig = '0001.png'

plt.close("all")

# Carregar e preparar os dados
data = pd.read_csv(file)
data_ordenada = data.copy()
metadata = 'timestamp'
origem = 'origem'
destino = 'destino'

# Ordenar por timestamp
data_ordenada[metadata] = pd.to_datetime(data_ordenada[metadata], dayfirst=False)
data_ordenada.sort_values(by=metadata, inplace=True)
data_ordenada.reset_index(inplace=True, drop=True)

# Selecionar colunas relevantes
data = data[[metadata, origem, destino]]
data[metadata] = pd.to_datetime(data[metadata], dayfirst=False)
data['timestamp_seconds'] = (data[metadata] - data[metadata].min()).dt.total_seconds()

# Contar ocorrências
contagem_ocorrencias = data.groupby([origem, destino]).size()
data['contagem_ocorrencias'] = data.apply(lambda row: contagem_ocorrencias[(row[origem], row[destino])], axis=1)

# Selecionar características
X = data[['timestamp_seconds']].values

# Normalização
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Definir janela de tempo
janela = {'days': 0, 'hours': 0, 'minutes': 20}
num_baldes = sum(1 for i in range(len(data[metadata])-1) 
    if data[metadata][i+1] - data[metadata][i] > pd.Timedelta(**janela))

# Parâmetros para clustering
kmin = 2
kmax = num_baldes + 10
sil = []

# Versão otimizada sem matriz de distâncias completa
for k in tqdm(range(kmin, kmax+1), desc='Calculando melhor número de clusters'):
    # Usando MiniBatchKMeans para eficiência
    kmeans = MiniBatchKMeans(n_clusters=k, random_state=21, batch_size=1000).fit(X_scaled)
    labels = kmeans.labels_
    
    # Calculando silhueta sem matriz de distâncias
    sil.append(silhouette_score(X_scaled, labels))

# Encontrar melhor cluster
cluster_center = np.argmax(np.array(sil[3:])) + 3 if len(sil) > 3 else np.argmax(sil) + kmin

# Plotar resultados
plt.close('all')
plt.plot(range(kmin, kmax+1), sil)
plt.xlim(kmin, kmax+1)
plt.plot([cluster_center, cluster_center], [min(sil), max(sil)], '--', 
         label=f'cluster ideal calculado: {cluster_center}')
plt.xlabel('Number of clusters')
plt.ylabel('Silhouette Score')
plt.legend()
plt.savefig(fig)
plt.show()

# Clusterização final
kmeans = MiniBatchKMeans(n_clusters=cluster_center, batch_size=1000)
kmeans.fit(X_scaled)
clusters = kmeans.labels_
data['Cluster'] = clusters

# Visualização
plt.figure()
plt.scatter(data[metadata], np.zeros(len(data[metadata])), c=clusters, cmap='viridis')
plt.xlabel('Timestamp')
plt.title(f"Janela: {janela['days']}d {janela['hours']}h {janela['minutes']}min - {cluster_center} clusters")
plt.show()

# Organizar resultados
baldes = {cluster: [] for cluster in set(clusters)}
for _, row in data.iterrows():
    baldes[row['Cluster']].append((row[origem], row[destino]))

# Exibir resultados
for i, bucket in enumerate(baldes.values()):
    print(f"Balde {i} de tamanho {len(bucket)}")
