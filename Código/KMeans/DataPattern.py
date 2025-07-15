import pandas as pd
import random
import os

def obter_valores_unicos_por_coluna(df):
    """Obtém os valores únicos de cada coluna do DataFrame."""
    valores_unicos = {}
    for coluna in df.columns:
        valores_unicos[coluna] = df[coluna].unique().tolist()
    return valores_unicos

def gerar_padroes_sequenciais(valores_unicos_por_coluna, num_padroes=3):
    """Gera padrões sequenciais (antecedente -> consequente) aleatoriamente."""
    padroes = []
    colunas = list(valores_unicos_por_coluna.keys())
    for _ in range(num_padroes):
        if len(colunas) >= 2:
            coluna_antecedente = random.choice(colunas)
            colunas_consequente_possiveis = [c for c in colunas if c != coluna_antecedente]
            if colunas_consequente_possiveis:
                coluna_consequente = random.choice(colunas_consequente_possiveis)
                valor_antecedente = random.choice(valores_unicos_por_coluna[coluna_antecedente])
                valor_consequente = random.choice(valores_unicos_por_coluna[coluna_consequente])
                padroes.append({'antecedente': valor_antecedente, 'coluna_antecedente': coluna_antecedente,
                                 'consequente': valor_consequente, 'coluna_consequente': coluna_consequente})
    return padroes

def inserir_padroes_sequenciais_repetidos(df, padroes):
    """Insere os padrões sequenciais aleatoriamente no DataFrame com repetições aleatórias."""
    df_modificado = df.copy()
    padroes_inseridos_info = []

    for padrao in padroes:
        num_repeticoes = random.randint(4, 10)
        for _ in range(num_repeticoes):
            linha_aleatoria = random.randint(0, len(df_modificado) - 1)
            antecedente = padrao['antecedente']
            coluna_antecedente = padrao['coluna_antecedente']
            consequente = padrao['consequente']
            coluna_consequente = padrao['coluna_consequente']

            antecedente_original = df_modificado.at[linha_aleatoria, coluna_antecedente]
            df_modificado.at[linha_aleatoria, coluna_antecedente] = antecedente

            consequente_original = df_modificado.at[linha_aleatoria, coluna_consequente]
            df_modificado.at[linha_aleatoria, coluna_consequente] = consequente

            padroes_inseridos_info.append({
                'padrao': padrao,
                'linha': linha_aleatoria,
                'antecedente_original': antecedente_original,
                'consequente_original': consequente_original,
                'antecedente_final': df_modificado.at[linha_aleatoria, coluna_antecedente],
                'consequente_final': df_modificado.at[linha_aleatoria, coluna_consequente],
                'repeticao': _ + 1  # Adiciona o número da repetição
            })

    # Agrupar informações por padrão para contar as repetições
    contagem_repeticoes_por_padrao = {}
    for info in padroes_inseridos_info:
        padrao_tuple = (info['padrao']['antecedente'], info['padrao']['coluna_antecedente'],
                        info['padrao']['consequente'], info['padrao']['coluna_consequente'])
        if padrao_tuple not in contagem_repeticoes_por_padrao:
            contagem_repeticoes_por_padrao[padrao_tuple] = 0
        contagem_repeticoes_por_padrao[padrao_tuple] += 1

    return df_modificado, padroes_inseridos_info, contagem_repeticoes_por_padrao

def exportar_info_padroes_sequenciais_repetidos_para_txt(padroes_inseridos_info, contagem_repeticoes_por_padrao, nome_arquivo):
    """Exporta informações detalhadas sobre os padrões sequenciais inseridos (com contagem de repetições) para um arquivo TXT."""
    nome_base = os.path.splitext(nome_arquivo)[0]
    nome_arquivo_txt = f"{nome_base}_padroes_sequenciais_inseridos.txt"
    with open(nome_arquivo_txt, 'w') as arquivo:
        arquivo.write("Informações Detalhadas dos Padrões Sequenciais Inseridos (com Repetições):\n\n")
        for (antecedente, coluna_antecedente, consequente, coluna_consequente), count in contagem_repeticoes_por_padrao.items():
            arquivo.write(f"Padrão (Antecedente -> Consequente): {antecedente} (na coluna '{coluna_antecedente}') -> {consequente} (na coluna '{coluna_consequente}')\n")
            arquivo.write(f"Repetições: {count}\n")
            arquivo.write("-" * 50 + "\n")

        arquivo.write("\nDetalhes das Inserções Individuais:\n\n")
        for info in padroes_inseridos_info:
            arquivo.write(f"Padrão (Antecedente -> Consequente): {info['padrao']['antecedente']} (na coluna '{info['padrao']['coluna_antecedente']}') -> {info['padrao']['consequente']} (na coluna '{info['padrao']['coluna_consequente']}')\n")
            arquivo.write(f"Linha: {info['linha']}\n")
            arquivo.write(f"Antecedente Original (Coluna '{info['padrao']['coluna_antecedente']}'): {info['antecedente_original']}\n")
            arquivo.write(f"Consequente Original (Coluna '{info['padrao']['coluna_consequente']}'): {info['consequente_original']}\n")
            arquivo.write(f"Antecedente Final (Coluna '{info['padrao']['coluna_antecedente']}'): {info['antecedente_final']}\n")
            arquivo.write(f"Consequente Final (Coluna '{info['padrao']['coluna_consequente']}'): {info['consequente_final']}\n")
            arquivo.write(f"Repetição Número: {info['repeticao']}\n")
            arquivo.write("-" * 50 + "\n")

    print(f"Informações detalhadas dos padrões sequenciais inseridos (com repetições) exportadas para '{nome_arquivo_txt}'")

if __name__ == "__main__":
    nome_arquivo_csv = input("Por favor, insira o nome do arquivo CSV (com a extensão .csv): ")
    try:
        df = pd.read_csv(nome_arquivo_csv)

        valores_unicos = obter_valores_unicos_por_coluna(df)
        num_padroes_a_gerar = 3
        padroes_gerados = gerar_padroes_sequenciais(valores_unicos, num_padroes_a_gerar)

        df_modificado, padroes_inseridos_info, contagem_repeticoes = inserir_padroes_sequenciais_repetidos(df.copy(), padroes_gerados)

        # Exportar o novo CSV modificado
        nome_base = os.path.splitext(nome_arquivo_csv)[0]
        nome_arquivo_csv_novo = f"{nome_base}_com_padroes_sequenciais.csv"
        df_modificado.to_csv(nome_arquivo_csv_novo, index=False)
        print(f"Arquivo CSV com os padrões sequenciais inseridos exportado para '{nome_arquivo_csv_novo}'")

        # Exportar informações detalhadas dos padrões sequenciais para TXT
        exportar_info_padroes_sequenciais_repetidos_para_txt(padroes_inseridos_info, contagem_repeticoes, nome_arquivo_csv)

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo_csv}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")