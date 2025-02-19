import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.preprocessing import StandardScaler
from math import sqrt, floor
from tqdm import tqdm
import fim
from time import time

class ruleFinder:
    def __init__(self, janela_tempo, min_repetition, min_confidence ):
        self.dataset = None
        self.metadata = None
        self.origem = None
        self.destino = None
        self.dados_com_cluster = None
        self.baldes = []
        self.janela_tempo = janela_tempo
        self.min_repetition = min_repetition
        self.min_confidence  = min_confidence 
       
    def set_dataset(self, dataset):
        self.dataset = dataset

    def set_infos_dados(self, metadata, origem, destino):
        self.metadata = metadata
        self.origem = origem
        self.destino = destino
    
    def set_infos_regras(self, janela_tempo, min_repetition, min_confidence ):
        self.janela_tempo = janela_tempo
        self.min_repetition = min_repetition
        self.min_confidence  = min_confidence 

    def kmeansBucketGenerator(self):
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.values.html
        # https://scikit-learn.org/stable/modules/preprocessing.html
        # https://towardsdatascience.com/advanced-k-means-controlling-groups-sizes-and-selecting-features-a998df7e6745
        metadata = self.metadata
        origem = self.origem
        destino = self.destino
        dataset = self.dataset
        
        dataset[metadata] = pd.to_datetime(dataset[metadata], dayfirst=True)
        dataset['timestamp_seconds'] = (dataset[metadata] - dataset[metadata].min()).dt.total_seconds()
        # colocar em ordem crescente de timestamp
        dataset.sort_values(by=metadata, inplace=True)
        dataset.reset_index(inplace=True, drop=True)


        # contar o numero de vezes que cada item (coluna 0, coluna 1) aparece
        contagem_ocorrencias = dataset.groupby([origem, destino]).size()
        dataset['contagem_ocorrencias'] = dataset.apply(lambda row: contagem_ocorrencias[(row[origem], row[destino])], axis=1)
        # #remove linhas com ocorrencias menores que 2
        dataset = dataset.loc[dataset['contagem_ocorrencias'] >= 2]
        dataset.reset_index(inplace=True, drop=True)

        # Selecionar características relevantes, neste caso, a coluna 'timestamp_seconds' e o numero de vezes que cada item aparece
        # X = dataset[['timestamp_seconds', 'contagem_ocorrencias']].values
        X = dataset[['timestamp_seconds']].values
     
        # Normalização dos dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # calcular a matriz de distancias
        # se trata da norma L2, mas como temos um dado 1D,
        # temos que a norma é equivalente ao valor absoluto de cada elemento 
        # da única componente
        Xi, Xj = np.meshgrid(X_scaled, X_scaled)
        distancias = np.abs(Xi - Xj) 

        # janela de tempo dada pelo usuario dependendo da natureza dos dados
        ## DEVE SER ADICIONADO AO WEB GUI
        janela = {'days': 0, 'hours': 2, 'minutes': 00}

        # numero de baldes que seriam gerados caso fosse usado a janela de tempo
        num_baldes = 0
        for i in range(0, len(dataset[metadata])-1):
            if dataset[metadata][i+1] - dataset[metadata][i] > pd.Timedelta(days=float(janela['days']), hours=float(janela['hours']), minutes=float(janela['minutes'])):
                num_baldes += 1

        # calcular o numero de clusters ideal atraves da distancia entre os pontos e seus centroides
        # atribui o kmin e kmax de acordo com o numero de baldes que seriam gerados
        kmin = 2
        kmax = num_baldes
        sil = []

        for k in tqdm(range(kmin, kmax+1), desc='Calculando melhor numero de clusters'):
            kmeans = KMeans(n_clusters=k, random_state=32).fit(X_scaled)
            labels = kmeans.labels_
            sil.append(silhouette_score(distancias, labels, metric='precomputed'))

        # pegar o cluster com o maior coeficiente de silhueta e plotar
        best_cluster = sil.index(max(sil))
        print(f'Melhor numero de clusters: {best_cluster}')


        # plt.plot(range(kmin, kmax+1), sil)
        # plt.xlabel('Number of clusters')
        # plt.ylabel('Silhouette Score')
        # plt.show()

        # https://stackoverflow.com/questions/28344660/how-to-identify-cluster-labels-in-kmeans-scikit-learn
        # mostrar os clusters de cada linha de acordo com o melhor cluster
        # como a primeira posicao do vetor esta associado a kmin, basta:
        kmeans = KMeans(n_clusters=best_cluster+kmin)
        kmeans.fit(X_scaled)
        labels = kmeans.labels_

        # #adicionar a coluna de clusters ao dataframe
        dataset['Cluster'] = labels # some improper dataset handling
        # #plot dos clusters em um grafico 2D onde y = 0
        # plt.scatter(dataset[metadata], np.zeros(len(dataset[metadata])), c=clusters, cmap='viridis')
        # plt.xlabel('Timestamp')
        # plt.show()
        self.dados_com_cluster = dataset

        dataset = dataset[[origem, destino, 'Cluster']]
        dataset.to_csv('dataset.csv')
        # test this out later* https://stackoverflow.com/questions/77623855/how-to-match-labels-and-their-cluster-point-in-k-means-clusters
        baldes = {}
        for index, row in dataset.iterrows():
            #print(list(row.values))
            if row['Cluster'] not in baldes:
                baldes[row['Cluster']] = []
            baldes[row['Cluster']].append((row[origem], row[destino]))

        all_buckets = []
        for balde in baldes:
            all_buckets.append(baldes[balde])

        self.baldes = all_buckets
        #i = 0
        # for bucket in all_buckets:
        #     print(f"Balde {i} de tamanho {len(bucket)}: {bucket}", '\n')
        #     i += 1

    def assoctiationRulesFinder(self):
        # https://andrewm4894.com/2020/09/29/market-basket-analysis-in-python/
        all_buckets = self.baldes

        print("Generating association rules through Apriori")
        min_repetition = self.min_repetition
        min_confidence  = self.min_confidence *100
        # Get classification rules by pyFim. From the pyFim doc:
        # [...] function arules for generating association rules
        # (simplified interface compared to apriori, eclat and fpgrowth,
        # which can also be used to generate association rules).

        columns_names = ['Consequente', 'Antecedente', 'FR', 'FA', 'FC', 'Conf']
        reordered_columns_names = ['Antecedente', 'Consequente', 'FR', 'FA', 'FC', 'Conf']

        ti = time()
        borgelt_rules = fim.arules(all_buckets, supp=-int(min_repetition), conf=min_confidence, report='abhC', zmin=2)
        borgelt_rules_df = pd.DataFrame(borgelt_rules, columns=columns_names)
        borgelt_rules_df = borgelt_rules_df[reordered_columns_names]
        # borgelt_rules_df.to_csv('association_rulesDF/association_rules_arules.csv')
        print(f"Elapsed time \t(Arules)\t: {time() - ti} s")

        ti = time()
        borgelt_rules_fpgrowth = fim.fpgrowth(all_buckets, supp=-int(min_repetition), conf=min_confidence,
                                              report='abhC', zmin=2, target='r')
        borgelt_rules_df_fpgrowth  = pd.DataFrame(borgelt_rules_fpgrowth, columns=columns_names)
        borgelt_rules_df_fpgrowth = borgelt_rules_df_fpgrowth[reordered_columns_names]
        # borgelt_rules_df_fpgrowth.to_csv('association_rulesDF/association_rules_fpgrowth.csv')
        print(f"Elapsed time \t(fpgrowth)\t: {time() - ti} s")

        ti = time()
        borgelt_rules_apriori = fim.apriori(all_buckets, supp=-int(min_repetition), conf=min_confidence, report='abhC',
                                            zmin=2, target='r')
        borgelt_rules_df_apriori  = pd.DataFrame(borgelt_rules_apriori, columns=columns_names)
        borgelt_rules_df_apriori = borgelt_rules_df_apriori[reordered_columns_names]
        # borgelt_rules_df_apriori.to_csv('association_rulesDF/association_rules_apriori.csv')
        print(f"Elapsed time \t(apriori)\t: {time() - ti} s")

        ti = time()
        borgelt_rules_eclat = fim.eclat(all_buckets, supp=-int(min_repetition), conf=min_confidence, report='abhC',
                                        zmin=2, target='r')
        borgelt_rules_df_eclat  = pd.DataFrame(borgelt_rules_eclat, columns=columns_names)
        borgelt_rules_df_eclat = borgelt_rules_df_eclat[reordered_columns_names]
        # borgelt_rules_df_eclat.to_csv('association_rulesDF/association_rules_eclat.csv')
        print(f"Elapsed time \t(eclat)\t: {time() - ti} s")


        t0 = time()
        #truncar conf para 2 casas decimais
        borgelt_rules_df['Conf'] = borgelt_rules_df['Conf'].apply(lambda x: round(x, 2))

        borgelt_rules_df = borgelt_rules_df.loc[borgelt_rules_df['FR'] >= int(min_repetition)]
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
        print(f"Elapsed time \t(rest of code)\t: {time() - ti} s")

        # Resultado final
        #print(rules_found_df)
        return rules_found_df