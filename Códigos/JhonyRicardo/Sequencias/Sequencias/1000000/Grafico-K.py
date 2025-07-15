import matplotlib.pyplot as plt
import re
import os

def extract_target_patterns(patterns_file):
    """Extrai apenas os padrões XXXX => YYYY do arquivo de padrões"""
    target_patterns = set()
    with open(patterns_file, 'r') as f:
        for line in f:
            if '=>' in line:
                # Extrai o padrão no formato "XXXX => YYYY"
                pattern = line.split('. ')[1].split(' - ')[0].strip()
                target_patterns.add(pattern)
    return target_patterns

def find_k_with_all_patterns(result_file, target_patterns):
    """Encontra os K onde todos os padrões alvo aparecem"""
    k_matches = []
    current_k = None
    found_patterns = set()
    
    with open(result_file, 'r') as f:
        for line in f:
            if 'Resultados para K = ' in line:
                try:
                    # Verifica se já temos um K acumulado
                    if current_k is not None and found_patterns.issuperset(target_patterns):
                        k_matches.append(current_k)
                    
                    # Extrai o novo K
                    k_part = line.split('K = ')[1]
                    current_k = int(k_part.split()[0].strip())
                    found_patterns = set()
                except (IndexError, ValueError):
                    continue
            
            # Verifica padrões nas regras
            elif '=>' in line and '(conf:' in line:
                pattern = line.split('(')[0].strip()
                if pattern in target_patterns:
                    found_patterns.add(pattern)
    
        # Verifica o último K
        if current_k is not None and found_patterns.issuperset(target_patterns):
            k_matches.append(current_k)
    
    return k_matches

def plot_results(k_matches, base_filename):
    """Gera e salva o gráfico com o mesmo nome base"""
    plt.figure(figsize=(12, 6))
    
    if k_matches:
        plt.scatter(k_matches, [1]*len(k_matches), 
                   color='green', s=200, alpha=0.7,
                   label=f'K com todos padrões (Total: {len(k_matches)})')
        plt.xlabel('Valores de K')
        plt.title('Valores de K que contêm TODOS os padrões alvo')
        plt.yticks([])
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.legend()
    else:
        plt.text(0.5, 0.5, 'Nenhum K contém todos os padrões', 
                ha='center', va='center', fontsize=14)
    
    plt.tight_layout()
    
    # Remove a extensão se existir e adiciona .png
    output_file = os.path.splitext(base_filename)[0] + '.png'
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Gráfico salvo como: {output_file}")

# Obter o nome base do arquivo (sem extensão)
base_name = input("Digite o nome base dos arquivos: ").strip()
patterns_file = base_name + '.txt'
result_file = 'resultados_kmeans_apriori.txt'  # Mantido fixo conforme seu requisito

try:
    # Verifica se o arquivo de padrões existe
    if not os.path.exists(patterns_file):
        raise FileNotFoundError(f"Arquivo {patterns_file} não encontrado")
    
    # Processamento
    targets = extract_target_patterns(patterns_file)
    print(f"Padrões alvo encontrados: {targets}")
    
    matching_ks = find_k_with_all_patterns(result_file, targets)
    print(f"Valores de K com todos os padrões: {matching_ks}")
    
    # Gera e salva o gráfico
    plot_results(matching_ks, base_name)
    
except FileNotFoundError as e:
    print(f"Erro: {e}")
except Exception as e:
    print(f"Erro inesperado: {str(e)}")