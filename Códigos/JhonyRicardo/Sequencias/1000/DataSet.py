import random
from datetime import datetime, timedelta
import csv

def gerar_timestamp_aleatorio(data_inicio, data_fim):
    """Gera um timestamp aleatório entre duas datas"""
    delta = data_fim - data_inicio
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return (data_inicio + timedelta(seconds=random_seconds)).strftime('%Y-%m-%d %H:%M:%S')

def gerar_dados(num_linhas):
    """Gera dados aleatórios no formato especificado"""
    data_inicio = datetime(2025, 4, 1)
    data_fim = datetime(2025, 6, 1)  # Período de 1 dia para os timestamps
    
    # Faixa de valores para origens e destinos (baseado no seu exemplo)
    min_valor = 30
    max_valor = 9000
    
    dados = []
    for _ in range(num_linhas):
        timestamp = gerar_timestamp_aleatorio(data_inicio, data_fim)
        origem = random.randint(min_valor, max_valor)
        destino = random.randint(min_valor, max_valor)
        dados.append([timestamp, origem, destino])
    
    # Ordena por timestamp (opcional)
    dados.sort(key=lambda x: x[0])
    
    return dados

def salvar_csv(dados, nome_arquivo='0003.csv'):
    """Salva os dados em um arquivo CSV"""
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'origem', 'destino'])  # Cabeçalho
        writer.writerows(dados)
    print(f'Arquivo {nome_arquivo} gerado com sucesso com {len(dados)} linhas.')
    
def gerar_numero_aleatorio():
    return random.randint(850, 1350)

def main():
    try:
        #num_linhas = int(input("Quantas linhas de dados você deseja gerar? "))
        #if num_linhas <= 0:
        #    print("Por favor, digite um número maior que zero.")
        #    return
        
        dados = gerar_dados(gerar_numero_aleatorio())
        salvar_csv(dados)
        
    except ValueError:
        print("Por favor, digite um número válido.")

if __name__ == "__main__":
    main()