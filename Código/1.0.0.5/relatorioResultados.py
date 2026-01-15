import os
import re
from typing import Dict, List, Tuple

def processar_arquivos(arquivos: List[str], diretorio: str) -> Dict[str, any]:

    resultados = {
        'total_arquivos': len(arquivos),
        'total_testes': 0,
        'testes_positivos': 0,
        'testes_negativos': 0,
        'taxa_sucesso': 0.0,
        'arquivos_processados': 0,
        'detalhes_por_arquivo': []
    }

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(diretorio, arquivo)

        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()

            # Processa este arquivo
            info_arquivo = processar_arquivo_individual(conteudo, arquivo)
            resultados['detalhes_por_arquivo'].append(info_arquivo)

            # Atualiza contadores gerais
            resultados['total_testes'] += info_arquivo['total_testes']
            resultados['testes_positivos'] += info_arquivo['testes_positivos']
            resultados['testes_negativos'] += info_arquivo['testes_negativos']
            resultados['arquivos_processados'] += 1

        except FileNotFoundError:
            print(f"Arquivo não encontrado: {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao processar {arquivo}: {e}")
    
    resultados['total_testes'] = len(info_arquivo['arquivos_processados'])
    
    # Calcula taxa de sucesso
    if resultados['total_testes'] > 0:
        resultados['taxa_sucesso'] = (resultados['testes_positivos'] / resultados['total_testes']) * 100

    return resultados

def processar_arquivo_individual(conteudo: str, nome_arquivo: str) -> Dict[str, any]:
    """
    Processa o conteúdo de um único arquivo Apriori.
    """
    # Extrai parâmetros do nome do arquivo
    parametros = extrair_parametros_do_nome(nome_arquivo)
    
    # Divide o conteúdo por testes individuais
    testes = re.split(r'=== Análise detalhada para teste ', conteudo)
    testes = [teste for teste in testes if teste.strip()]

    info_arquivo = {
        'arquivo': nome_arquivo,
        'parametros': parametros,
        'total_testes': len(testes),
        'testes_positivos': 0,
        'testes_negativos': 0,
        'detalhes_testes': []
    }

    for teste in testes:
        resultado_teste = analisar_teste_individual(teste)
        info_arquivo['detalhes_testes'].append(resultado_teste)

        if resultado_teste['todos_encontrados']:
            info_arquivo['testes_positivos'] += 1
        else:
            info_arquivo['testes_negativos'] += 1

    return info_arquivo

def analisar_teste_individual(conteudo_teste: str) -> Dict[str, any]:
    """
    Analisa um único teste dentro do arquivo.
    """
    # Extrai o nome do teste
    linhas = conteudo_teste.split('\n')
    nome_teste = linhas[0].replace('===', '').strip() if linhas else "Desconhecido"

    # Verifica se todos os padrões foram encontrados
    todos_encontrados = False
    confiancas = []
    suportes = []
    padroes_encontrados = 0

    for linha in conteudo_teste.split('\n'):
        linha = linha.strip()

        # Verifica resultado final
        if "Todos os padrões foram encontrados?" in linha:
            todos_encontrados = "Sim" in linha

        # Extrai confiança e suporte
        elif "Confiança:" in linha:
            try:
                confianca = float(linha.split(':')[1].strip())
                confiancas.append(confianca)
            except (ValueError, IndexError):
                pass

        elif "Suporte:" in linha:
            try:
                suporte = float(linha.split(':')[1].strip())
                suportes.append(suporte)
            except (ValueError, IndexError):
                pass

        # Conta padrões encontrados
        elif "Encontrado:" in linha and "repetições completas" in linha:
            padroes_encontrados += 1

    return {
        'nome_teste': nome_teste,
        'todos_encontrados': todos_encontrados,
        'total_padroes': padroes_encontrados,
        'confianca_media': sum(confiancas) / len(confiancas) if confiancas else 0,
        'suporte_medio': sum(suportes) / len(suportes) if suportes else 0,
        'confiancas': confiancas,
        'suportes': suportes
    }

def extrair_parametros_do_nome(nome_arquivo: str) -> Dict[str, any]:
    """
    Extrai parâmetros do nome do arquivo.
    """
    nome = nome_arquivo.replace('Resultado_', '').replace('.txt', '')
    partes = nome.split('_')

    if len(partes) >= 6:
        return {
            'registros': int(partes[0]),
            'padroes': int(partes[1]),
            'itens': int(partes[2]),
            'repeticoes': int(partes[3]),
            'intervalo': int(partes[4]),
            'teste': partes[5]
        }
    return {}

def gerar_relatorio_txt(resultados: Dict[str, any], arquivo_saida: str):
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("RELATÓRIO DE ANÁLISE DOS TESTES APRIORI\n")
        f.write("=" * 60 + "\n\n")

        # Estatísticas gerais
        f.write("ESTATÍSTICAS GERAIS:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total de arquivos processados: {resultados['arquivos_processados']}/{resultados['total_arquivos']}\n")
        f.write(f"Total de testes analisados: {resultados['total_testes']}\n")
        f.write(f"Testes positivos (todos padrões encontrados): {resultados['testes_positivos']}\n")
        f.write(f"Testes negativos: {resultados['testes_negativos']}\n")
        f.write(f"Taxa de sucesso: {resultados['taxa_sucesso']:.2f}%\n\n")

        # Detalhes por arquivo
        f.write("DETALHES POR ARQUIVO:\n")
        f.write("=" * 60 + "\n")

        for detalhe in resultados['detalhes_por_arquivo']:
            f.write(f"\nArquivo: {detalhe['arquivo']}\n")
            f.write(f"Parâmetros: {detalhe['parametros']}\n")
            f.write(f"Testes no arquivo: {detalhe['total_testes']}\n")
            f.write(f"Testes positivos: {detalhe['testes_positivos']}\n")
            f.write(f"Testes negativos: {detalhe['testes_negativos']}\n")
            f.write(f"Taxa de sucesso: {(detalhe['testes_positivos']/detalhe['total_testes']*100 if detalhe['total_testes'] > 0 else 0):.2f}%\n")

            # Estatísticas dos testes deste arquivo
            if detalhe['detalhes_testes']:
                confiancas = [t['confianca_media'] for t in detalhe['detalhes_testes'] if t['confianca_media'] > 0]
                suportes = [t['suporte_medio'] for t in detalhe['detalhes_testes'] if t['suporte_medio'] > 0]

                if confiancas:
                    f.write(f"Confiança média: {sum(confiancas)/len(confiancas):.6f}\n")
                if suportes:
                    f.write(f"Suporte médio: {sum(suportes)/len(suportes):.8f}\n")

            f.write("-" * 40 + "\n")

        # Resumo final
        f.write("\n" + "=" * 60 + "\n")
        f.write("RESUMO FINAL\n")
        f.write("=" * 60 + "\n")
        f.write(f"Arquivos analisados com sucesso: {resultados['arquivos_processados']}\n")
        f.write(f"Total de testes executados: {resultados['total_testes']}\n")
        f.write(f"Taxa global de sucesso: {resultados['taxa_sucesso']:.2f}%\n")

        if resultados['total_testes'] > 0:
            f.write(f"Média de testes por arquivo: {resultados['total_testes']/resultados['arquivos_processados']:.1f}\n")
