# get a dataset from the files and make clusters
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.preprocessing import StandardScaler
from math import sqrt, floor
from tqdm import tqdm
from fim import arules

# fazer clusterizacao hierarquica
# C:\...\datasets\Divisão [MConverter.eu].csv
data = pd.read_csv('datasets\Repasses [MConverter.eu].csv')
data_ordenada = data.copy()
raw_data = data.copy()
metadata = 'DataHora'
origem = 'Conta Origem'
destino = 'Conta Destino'

# colocar uma COPIA do dataset em ordem cronologica e salvar em csv
data_ordenada[metadata] = pd.to_datetime(data_ordenada[metadata], dayfirst=True)
data_ordenada.sort_values(by=metadata, inplace=True)
data_ordenada.reset_index(inplace=True, drop=True)
data_ordenada.to_csv('Repasses_ordenada.csv', index=False)



# keep only the columns that are going to be used
data = data[[metadata, origem, destino]]

data[metadata] = pd.to_datetime(data[metadata], dayfirst=True)
data['timestamp_seconds'] = (data[metadata] - data[metadata].min()).dt.total_seconds()


# colocar em ordem crescente de timestamp
data.sort_values(by=metadata, inplace=True)
data.reset_index(inplace=True, drop=True)


# contar o numero de vezes que cada item (coluna 0, coluna 1) aparece
contagem_ocorrencias = data.groupby([origem, destino]).size()
data['contagem_ocorrencias'] = data.apply(lambda row: contagem_ocorrencias[(row[origem], row[destino])], axis=1)

# #remove colunas com ocorrencias menores que 2
# data = data.loc[data['contagem_ocorrencias'] >= 2]
# data.reset_index(inplace=True, drop=True)

# Selecionar características relevantes, neste caso, a coluna 'timestamp_seconds' e o numero de vezes que cada item aparece
# X = data[['timestamp_seconds', 'contagem_ocorrencias']].values
X = data[['timestamp_seconds']].values

# Normalização dos dados
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# janela de tempo dada pelo usuario dependendo da natureza dos dados
janela = {'days': 0, 'hours': 0, 'minutes': 10}

# numero de baldes que seriam gerados caso fosse usado a janela de tempo
num_baldes = 0
for i in range(0, len(data[metadata])-1):
    if data[metadata][i+1] - data[metadata][i] > pd.Timedelta(days=float(janela['days']), hours=float(janela['hours']), minutes=float(janela['minutes'])):
        num_baldes += 1

# calcular o numero de clusters ideal atraves da distancia entre os pontos e seus centroides
# atribui o kmin e kmax de acordo com o numero de baldes que seriam gerados
kmin = 2
kmax = num_baldes + 10
sil = []

# calcular a matriz de distancias
distancias = np.zeros((len(X_scaled), len(X_scaled)))
for i in range(len(X_scaled)):
    for j in range(len(X_scaled)):
        distancias[i][j] = sqrt((X_scaled[i][0] - X_scaled[j][0])**2)

for k in tqdm(range(kmin, kmax+1), desc='Calculando melhor numero de clusters'):
    kmeans = KMeans(n_clusters = k, random_state=21).fit(X_scaled)
    labels = kmeans.labels_
    sil.append(silhouette_score(distancias, labels, metric='precomputed'))

# pegar o cluster com o maior coeficiente de silhueta e plotar
best_cluster = sil.index(max(sil)) + kmin
print(f'Melhor numero de clusters: {best_cluster}')

#plt.plot(range(kmin, kmax+1), sil)
#plt.xlabel('Number of clusters')
#plt.ylabel('Silhouette Score')
#plt.title("num baldes: " + str(num_baldes))
#plt.show()

# plt.imshow(distancias)
# plt.colorbar()
# plt.show()

# mostrar os clusters de cada linha de acordo com o melhor cluster
kmeans = KMeans(n_clusters=best_cluster)
kmeans.fit(X_scaled)
clusters = kmeans.labels_
data['Cluster'] = clusters

#plot dos clusters em um grafico 2D onde y = 0
plt.scatter(data[metadata], np.zeros(len(data[metadata])), c=clusters, cmap='viridis')
plt.xlabel('Timestamp')
plt.title("Janela: "+str(janela['days']) + "d " + str(janela['hours'])
          + "h " + str(janela['minutes']) + "min   " + str(best_cluster) + " balde(s)")
plt.show()



data = data[[origem, destino, 'Cluster']]
print(data)

baldes = {}
for index, row in data.iterrows():
    #print(list(row.values))
    if row['Cluster'] not in baldes:
        baldes[row['Cluster']] = []
    baldes[row['Cluster']].append((row[origem], row[destino]))

all_buckets = []
for balde in baldes:
    all_buckets.append(baldes[balde])

#print(all_buckets)
i = 0
for bucket in all_buckets:
    print(f"Balde {i} de tamanho {len(bucket)}: {bucket}", '\n')
    i += 1



# apriori
print("Apriori")
min_rep = 6
min_conf = 75
borgelt_rules = arules(all_buckets,supp=-int(min_rep), conf=min_conf, report='abhC' , zmin=2)

# print("Number of rules found: ", len(borgelt_rules))
# print(borgelt_rules)

columns_names = ['Consequente', 'Antecedente', 'FR', 'FA', 'FC', 'Conf']
reordered_columns_names = ['Antecedente', 'Consequente', 'FR', 'FA', 'FC', 'Conf']
borgelt_rules_df = pd.DataFrame(borgelt_rules, columns=columns_names)
borgelt_rules_df = borgelt_rules_df[reordered_columns_names]

borgelt_rules_df = borgelt_rules_df.loc[borgelt_rules_df['FR'] >= int(min_rep)]
borgelt_rules_df.reset_index(inplace=True, drop=True)



# Função para verificar se um conjunto é subconjunto de outro
def is_subset(a, b):
    return set(a).issubset(set(b))

# Lista para armazenar os índices das linhas a serem removidas
indices_remover = []

# Iterar sobre cada linha
for i, row in borgelt_rules_df.iterrows():
    antecedente_atual = row['Antecedente']
    consequente_atual = row['Consequente']
    
    # Verificar se existe outra linha com antecedente subconjunto e mesmo consequente
    for j, other_row in borgelt_rules_df.iterrows():
        if i != j:  # Evitar comparação com a mesma linha
            antecedente_outro = other_row['Antecedente']
            consequente_outro = other_row['Consequente']
            
            if is_subset(antecedente_atual, antecedente_outro) and consequente_atual == consequente_outro:
                # Além disso, verificar se as outras métricas são iguais ou menores
                if other_row['FR'] >= row['FR'] and other_row['FA'] >= row['FA'] and other_row['FC'] >= row['FC'] and other_row['Conf'] >= row['Conf']:
                    indices_remover.append(i)
                break  # Parar de procurar outras correspondências

# Remover as linhas com os índices identificados
rules_found_df = borgelt_rules_df.drop(indices_remover)
rules_found_df.reset_index(inplace=True, drop=True)

# Resultado final
print(rules_found_df)
rules_found_df.to_csv('regras_encontradas_novo.csv')


#verificar quais regras tem os mesmos elementos, independente da ordem
# antecedentes = []
# consequentes = []
# elementos = []
# for index, row in rules_found_df.iterrows():
#     elementos = row['Antecedente'] + row['Consequente']