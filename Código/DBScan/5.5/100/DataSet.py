import random
from datetime import datetime, timedelta
import csv

def gerar_timestamp_aleatorio(data_inicio, data_fim):
    delta = data_fim - data_inicio
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return (data_inicio + timedelta(seconds=random_seconds)).strftime('%Y-%m-%d %H:%M:%S')

def gerar_dados(num_linhas):
    data_inicio = datetime(2025, 5, 15)
    data_fim = datetime(2025, 6, 15)  # Período de 1 dia para os timestamps
    
    # Faixa de valores para origens e destinos (baseado no seu exemplo)
    min_valor = 30
    max_valor = 9999
    
    dados = []
    for _ in range(num_linhas):
        timestamp = gerar_timestamp_aleatorio(data_inicio, data_fim)
        origem = random.randint(min_valor, max_valor)
        destino = random.randint(min_valor, max_valor)
        dados.append([timestamp, origem, destino])
    
    # Ordena por timestamp (opcional)
    dados.sort(key=lambda x: x[0])
    
    return dados

def salvar_csv(dados, nome_arquivo='0001.csv'):
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'origem', 'destino'])  # Cabeçalho
        writer.writerows(dados)
    print(f'Arquivo {nome_arquivo} gerado com sucesso com {len(dados)} linhas.')

def main():
    try:
        num_linhas = int(input("Quantas linhas de dados você deseja gerar? "))
        if num_linhas <= 0:
            print("Por favor, digite um número maior que zero.")
            return
        
        dados = gerar_dados(num_linhas)
        salvar_csv(dados)
        
    except ValueError:
        print("Por favor, digite um número válido.")

if __name__ == "__main__":
    main()