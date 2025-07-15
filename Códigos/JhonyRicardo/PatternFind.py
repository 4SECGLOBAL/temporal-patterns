import pandas as pd
import numpy as np
import random
from itertools import combinations
from collections import defaultdict

def gerar_dados_com_padroes(num_transacoes=1000, num_itens=50, padroes=None):
    """
    Gera dados transacionais com padrões inseridos artificialmente
    
    Args:
        num_transacoes: Número total de transações
        num_itens: Número total de itens diferentes
        padroes: Lista de tuplas (antecedente, consequente, probabilidade)
    
    Returns:
        DataFrame com as transações
    """
    if padroes is None:
        # Padrões de exemplo
        padroes = [
            (['item1', 'item2'], 'item5', 0.9),  # item1 e item2 → item5 com 90% de chance
            (['item3'], 'item7', 0.8),          # item3 → item7 com 80% de chance
            (['item10', 'item15'], 'item20', 0.85)
        ]
    
    transacoes = []
    itens = [f'item{i}' for i in range(1, num_itens+1)]
    
    for _ in range(num_transacoes):
        transacao = set()
        
        # Adiciona itens aleatórios (1 a 5 itens por transação)
        num_itens_transacao = random.randint(1, 5)
        transacao.update(random.sample(itens, num_itens_transacao))
        
        # Insere padrões conforme as probabilidades
        for antecedente, consequente, prob in padroes:
            if all(item in transacao for item in antecedente):
                if random.random() < prob:
                    transacao.add(consequente)
        
        transacoes.append(list(transacao))
    
    return pd.DataFrame({'transacao': transacoes}), padroes

def identificar_padroes_inseridos(df, padroes_inseridos):
    """
    Identifica os padrões inseridos nos dados para validação
    
    Args:
        df: DataFrame com as transações
        padroes_inseridos: Lista de padrões inseridos
    
    Returns:
        Dicionário com estatísticas dos padrões
    """
    resultados = {}
    
    for antecedente, consequente, prob_inserida in padroes_inseridos:
        chave = f"{' & '.join(antecedente)} → {consequente}"
        
        # Conta ocorrências do antecedente
        mask_antecedente = df['transacao'].apply(lambda x: all(item in x for item in antecedente))
        total_antecedente = mask_antecedente.sum()
        
        # Conta ocorrências do antecedente + consequente
        mask_padrao = df['transacao'].apply(lambda x: all(item in x for item in antecedente) and consequente in x)
        total_padrao = mask_padrao.sum()
        
        # Calcula suporte e confiança observados
        suporte = total_padrao / len(df)
        confianca = total_padrao / total_antecedente if total_antecedente > 0 else 0
        
        resultados[chave] = {
            'probabilidade_inserida': prob_inserida,
            'suporte_observado': suporte,
            'confianca_observada': confianca,
            'ocorrencias_antecedente': total_antecedente,
            'ocorrencias_padrao': total_padrao
        }
    
    return resultados

def preparar_para_algoritmos(df, nome_arquivo='dados_transacionais.csv'):
    """
    Prepara os dados para algoritmos de mineração de regras
    
    Args:
        df: DataFrame com as transações
        nome_arquivo: Nome do arquivo de saída
    
    Returns:
        Caminho do arquivo salvo
    """
    # Salva no formato adequado para Apriori/FPGrowth
    df.to_csv(nome_arquivo, index=False)
    return nome_arquivo

def main():
    # 1. Gerar dados com padrões inseridos
    df, padroes_inseridos = gerar_dados_com_padroes()
    
    print("Padrões inseridos artificialmente:")
    for antecedente, consequente, prob in padroes_inseridos:
        print(f"{' & '.join(antecedente)} → {consequente} (prob: {prob})")
    print("\n")
    
    # 2. Identificar e mostrar estatísticas dos padrões inseridos
    estatisticas = identificar_padroes_inseridos(df, padroes_inseridos)
    
    print("Estatísticas dos padrões inseridos:")
    for padrao, stats in estatisticas.items():
        print(f"\nPadrão: {padrao}")
        print(f" - Probabilidade inserida: {stats['probabilidade_inserida']:.2f}")
        print(f" - Suporte observado: {stats['suporte_observado']:.4f}")
        print(f" - Confiança observada: {stats['confianca_observada']:.4f}")
        print(f" - Ocorrências do antecedente: {stats['ocorrencias_antecedente']}")
        print(f" - Ocorrências do padrão: {stats['ocorrencias_padrao']}")
    
    # 3. Preparar dados para algoritmos de mineração
    arquivo = preparar_para_algoritmos(df)
    print(f"\nDados salvos em '{arquivo}' pronto para Apriori/FPGrowth")

if __name__ == "__main__":
    main()