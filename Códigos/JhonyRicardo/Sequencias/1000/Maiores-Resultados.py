from collections import defaultdict
import re

def extract_patterns(file_path):
    pattern_counter = defaultdict(int)
    pattern_regex = re.compile(r"(.+?) => (.+?) \(conf: .+?, sup: .+?\)")
    
    with open(file_path, 'r') as file:
        for line in file:
            match = pattern_regex.search(line)
            if match:
                antecedents = match.group(1).strip()
                consequents = match.group(2).strip()
                pattern = f"{antecedents} => {consequents}"
                pattern_counter[pattern] += 1
                
    return pattern_counter

def save_top_patterns(pattern_counter, output_file, top_n=10):
    sorted_patterns = sorted(pattern_counter.items(), key=lambda x: x[1], reverse=True)
    
    with open(output_file, 'w') as file:
        file.write("Top 10 padrões mais repetidos:\n\n")
        for i, (pattern, count) in enumerate(sorted_patterns[:top_n], 1):
            file.write(f"{i}. {pattern} - {count} ocorrências\n")

# Arquivos de entrada e saída
input_file = 'resultados_kmeans_apriori.txt'  # Arquivo gerado pelo programa anterior
output_file = 'top_patterns.txt'

# Processar o arquivo e salvar os resultados
pattern_counter = extract_patterns(input_file)
save_top_patterns(pattern_counter, output_file)

print(f"Processo concluído. Os 10 padrões mais frequentes foram salvos em {output_file}")