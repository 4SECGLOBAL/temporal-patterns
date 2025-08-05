import re
from collections import defaultdict

def analyze_data(k, max_rule_files, output_file):
    """Analisa os arquivos de teste e verifica correspondências com o arquivo Apriori."""
    
    def try_read_file(filename):
        """Tenta ler um arquivo com diferentes codificações"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Não foi possível ler o arquivo {filename} com as codificações testadas")
    
    results = {
        'test_number': k,
        'pattern_groups': [],
        'all_patterns_found': True
    }
    
    # 1. Identificar todos os grupos de padrões dos arquivos de regras
    pattern_groups = []
    
    for i in range(1, max_rule_files + 1):
        rule_filename = f"{k}_{i}.txt"
        try:
            content = try_read_file(rule_filename)
            
            # Extrair todos os grupos de padrões
            events = re.split(r'=== Acontecimento \d+ ===', content)
            for event in events[1:]:
                pattern_content = re.search(r'Conteúdo:\s*(.+?)\s*Repetiç', event, re.DOTALL)
                if pattern_content:
                    patterns = re.findall(r'(\d+)\s*=>\s*(\d+)', pattern_content.group(1))
                    pattern_group = [f"{origem} => {destino}" for origem, destino in patterns]
                    if pattern_group not in pattern_groups:
                        pattern_groups.append(pattern_group)
                        
        except FileNotFoundError:
            print(f"Arquivo {rule_filename} não encontrado")
        except UnicodeDecodeError as e:
            print(f"Erro ao ler {rule_filename}: {str(e)}")
    
    # 2. Processar arquivo Apriori para extrair sequências e repetições
    apriori_filename = f"{k}Apriori.txt"
    
    try:
        apriori_content = try_read_file(apriori_filename)
        
        # Extrair todas as sequências com seus padrões e repetições
        sequences = []
        seq_matches = re.finditer(r'Sequência (\d+):(.*?)Repetições completas: (\d+)', apriori_content, re.DOTALL)
        
        for match in seq_matches:
            seq_num = int(match.group(1))
            seq_content = match.group(2)
            repetitions = int(match.group(3))
            
            # Extrair padrões desta sequência
            patterns = re.findall(r"\{'origem_(\d+)'\} -> \{'destino_(\d+)'\}", seq_content)
            seq_patterns = [f"{origem} => {destino}" for origem, destino in patterns]
            
            sequences.append({
                'seq_num': seq_num,
                'patterns': seq_patterns,
                'repetitions': repetitions
            })
            
    except FileNotFoundError:
        print(f"Arquivo {apriori_filename} não encontrado.")
        results['all_patterns_found'] = False
    
    # 3. Verificar cada grupo de padrões contra as sequências do Apriori
    for group_num, pattern_group in enumerate(pattern_groups, 1):
        group_found = False
        repetitions = 0
        
        # Procurar em todas as sequências do Apriori
        for sequence in sequences:
            # Verificar se todos os padrões do grupo estão nesta sequência
            if all(pattern in sequence['patterns'] for pattern in pattern_group):
                group_found = True
                repetitions = sequence['repetitions']
                break
        
        results['pattern_groups'].append({
            'group_num': group_num,
            'patterns': pattern_group,
            'found': group_found,
            'repetitions': repetitions
        })
        
        if not group_found:
            results['all_patterns_found'] = False
    
    # 4. Escrever resultados no arquivo de saída
    with open(output_file, 'a', encoding='utf-8') as out_file:
        out_file.write(f"\n\n=== Análise detalhada para teste {k} ===\n")
        out_file.write(f"Total de arquivos de regras processados: {max_rule_files}\n")
        
        out_file.write("\n=== OCORRÊNCIAS INDIVIDUAIS DOS PADRÕES ===\n")
        
        for group in results['pattern_groups']:
            out_file.write(f"\nPadrão {group['group_num']}:\n")
            for pattern in group['patterns']:
                out_file.write(f"   {pattern}\n")
            
            if group['found']:
                out_file.write(f"Encontrado: {group['repetitions']} repetições completas\n")
            else:
                out_file.write("Encontrado: Não\n")
        
        out_file.write("\n=== RESUMO DE CORRESPONDÊNCIAS ===\n")
        out_file.write(f"\nTodos os padrões foram encontrados? {'Sim' if results['all_patterns_found'] else 'Não'}\n")
    
    return results


import pandas as pd

def analyze_clusters(m):
    file_path = 'DEBUG.txt'
    # Lê o arquivo, assumindo que é separado por tabulações
    df = pd.read_csv(file_path, sep='\t')
    
    # Calcula o maior número de cluster
    max_cluster = df['cluster'].max()
    
    # Filtra clusters válidos (excluindo cluster 0 e onde valid_cluster é False)
    valid_clusters = df[(df['cluster'] != 0) & (df['valid_cluster'] == True)]
    
    if not valid_clusters.empty:
        avg_items_per_cluster = valid_clusters['cluster'].value_counts().mean()
    else:
        avg_items_per_cluster = 0
    
    # Conta linhas a serem removidas (outlier=True OU valid_cluster=False)
    outliers = df[(df['outlier'] == True) | (df['valid_cluster'] == False)].shape[0]
    
    out_file = "Clusters.txt"
    with open(out_file, 'a', encoding='utf-8') as out_file:
        out_file.write(f"\n=== Análise detalhada para cluster ===\n")
        out_file.write(f"Teste número {m}/10:\n")
        out_file.write(f"Número total de cluster: {max_cluster} clusters\n")
        out_file.write(f"Média de itens por cluster: {avg_items_per_cluster}\n")
        out_file.write(f"Número de outliers: {outliers}\n")

