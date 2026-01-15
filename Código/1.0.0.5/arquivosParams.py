import os
import re
from typing import List, Dict

# Tarefa 0.I: Matriz parâmetros
PARAMETROS = {
    'registros': [500, 1000, 2000, 5000, 10000, 50000, 100000, 200000],
    'padroes': [1, 2, 3, 4, 5],
    'itens': [3, 4, 5, 6, 7],
    'repeticoes': [3, 4, 5, 6, 7],
    'intervalo': [5, 10, 30, 60, 120, 180],
    'teste': ['001', '002', '003', '004', '005', '006', '007', '008', '009', '010']
}

# Tarefa 0.II: Mapeamento da posição dos parâmetros
POSICOES = {
    'registros': 0,
    'padroes': 1,
    'itens': 2,
    'repeticoes': 3,
    'intervalo': 4,
    'teste': 5
}

def filtrar_arquivos_por_parametro(diretorio: str, parametro: str, valor, extensao: str = "Apriori.txt") -> List[str]:
#   Encontrar todos os arquivos com um parâmetro específico

# Tarefa I. Conversão para string e obtenção do parâmetro

    if parametro not in POSICOES:
        raise ValueError(f"Parâmetro '{parametro}' não é válido. Opções: {list(POSICOES.keys())}")
    
    
    if parametro == 'teste':
        if valor < 10:
            valor_str = str("00"+str(valor))
            print(valor_str)
        else:
            valor_str = str("0"+str(valor))
            print(valor_str)
            
        if valor_str not in PARAMETROS[parametro]:
            raise ValueError(f"Valor '{valor_str}' não é válido para o parâmetro '{parametro}'. "
                           f"Opções: {PARAMETROS[parametro]}")
    else:
        valor_str = str(valor)

        if valor not in PARAMETROS[parametro]:
            raise ValueError(f"Valor '{valor}' não é válido para o parâmetro '{parametro}'. "
                           f"Opções: {PARAMETROS[parametro]}")    
    
#   Tarefa II. Encontrar a posição do parâmetro 
    posicao = POSICOES[parametro]
    
#   Tarefa III. Filtrar todos os arquivos encontrados
    try:
        todos_arquivos = os.listdir(diretorio)
    except FileNotFoundError:
        raise FileNotFoundError(f"Diretório '{diretorio}' não encontrado")
    
    arquivos_apriori = [f for f in todos_arquivos if f.endswith(extensao)]
    
    arquivos_filtrados = []
    
    for arquivo in arquivos_apriori:
        nome_sem_extensao = arquivo.replace(extensao, '')
        
#       Tarefa III.I. Divisão do nome por "_"
        partes = nome_sem_extensao.split('_')
        
        if len(partes) != 6:
            continue
        
#       Tarefa III.II. Verificação do valor
        if partes[posicao] == valor_str:
            arquivos_filtrados.append(arquivo)
    
    return arquivos_filtrados

# def filtrar_arquivos_por_multiplos_parametros(diretorio: str, filtros: Dict[str, any], extensao: str = "Apriori.txt") -> List[str]:
#     """
#     Filtra arquivos baseado em múltiplos parâmetros de forma eficiente.
#     """
#     # Validação dos filtros
#     for parametro, valor in filtros.items():
#         if parametro not in POSICOES:
#             raise ValueError(f"Parâmetro '{parametro}' não é válido. Opções: {list(POSICOES.keys())}")
#         if valor not in PARAMETROS[parametro]:
#             raise ValueError(f"Valor '{valor}' não é válido para o parâmetro '{parametro}'. "
#                            f"Opções: {PARAMETROS[parametro]}")
#     
#     # Lista todos os arquivos no diretório
#     try:
#         todos_arquivos = os.listdir(diretorio)
#     except FileNotFoundError:
#         raise FileNotFoundError(f"Diretório '{diretorio}' não encontrado")
#     
#     # Filtra arquivos que correspondem a TODOS os critérios
#     arquivos_filtrados = []
#     
#     for arquivo in todos_arquivos:
#         if not arquivo.endswith(extensao):
#             continue
#             
#         nome_sem_extensao = arquivo.replace(extensao, '')
#         partes = nome_sem_extensao.split('_')
#         
#         if len(partes) != 6:
#             continue
#         
#         # Verifica se o arquivo atende a TODOS os filtros
#         atende_todos = True
#         
#         for parametro, valor in filtros.items():
#             posicao = POSICOES[parametro]
#             
#             # Formata o valor corretamente
#             if parametro == 'teste':
#                 valor_esperado = f"{int(valor):03d}"
#             else:
#                 valor_esperado = str(valor)
#             
#             # Verifica se a parte corresponde
#             if partes[posicao] != valor_esperado:
#                 atende_todos = False
#                 break
#         
#         if atende_todos:
#             arquivos_filtrados.append(arquivo)
#     
#     return arquivos_filtrados

def listar_todos_arquivos_apriori(diretorio: str, extensao: str = "Apriori.txt") -> List[str]:
    
    try:
        todos_arquivos = os.listdir(diretorio)
        return [f for f in todos_arquivos if f.startswith(extensao)]
    except FileNotFoundError:
        return []

# Exemplos
if __name__ == "__main__":
    diretorio = "."  # Substitua pelo seu diretório
    
    # Arquivos disponíveis
    todos_arquivos = listar_todos_arquivos_apriori(diretorio)
    
    print(listar_todos_arquivos_apriori)
    
    print("\n" + "="*50 + "\n")
#     
#     try:
#         filtros = {'registros': 5000, 'padroes': 5}
#         arquivos_multiplos = filtrar_arquivos_por_multiplos_parametros(diretorio, filtros)
#         print("Arquivos com registros=5000 E padrões=5:")
#         for arquivo in arquivos_multiplos:
#             print(f"  - {arquivo}")
#     except Exception as e:
#         print(f"Erro: {e}")
#     
#     print("\n" + "="*50 + "\n")
#     
#     # Exemplo: Filtrar por três parâmetros - registros=100000, itens=6, repeticoes=7
#     try:
#         filtros = {'registros': 100000, 'itens': 6, 'repeticoes': 7}
#         arquivos_tres_parametros = filtrar_arquivos_por_multiplos_parametros(diretorio, filtros)
#         print("Arquivos com registros=100000, itens=6, repeticoes=7:")
#         for arquivo in arquivos_tres_parametros:
#             print(f"  - {arquivo}")
#     except Exception as e:
#         print(f"Erro: {e}")
#     
#     print("\n" + "="*50 + "\n")
#     
#     print("\n" + "="*50 + "\n")
# 
#     # Exemplo 4: Filtrar por teste = 3
#     try:
#         arquivos_teste = filtrar_arquivos_por_parametro(diretorio, 'padroes', 3)
#         print("Arquivos com teste = 3:")
#         for arquivo in arquivos_teste:
#             print(f"  - {arquivo}")
#     except Exception as e:
#         print(f"Erro: {e}")
# 
