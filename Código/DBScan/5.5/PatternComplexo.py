import pandas as pd
import random
from datetime import datetime, timedelta

def generate_random_patterns(input_file, output_file, num_patterns, repetitions, pattern_size):
    # Carregar o dataset original
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        return
    
    # Gerar padrões aleatórios com o tamanho especificado
    random_patterns = []
    for _ in range(num_patterns):
        pattern_sequence = []
        for _ in range(pattern_size):
            antecedent = random.randint(100, 9999)
            consequent = random.randint(100, 9999)
            pattern_sequence.append(f"{antecedent} => {consequent}")
        random_patterns.append(("\n    ".join(pattern_sequence), repetitions))
    
    # Converter timestamps para datetime para facilitar manipulação
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Gerar timestamps aleatórios dentro do intervalo existente
    min_time = df['timestamp'].min()
    max_time = df['timestamp'].max()
    time_range = (max_time - min_time).total_seconds()
    
    # Criar novos registros com os padrões aleatórios
    new_records = []
    for pattern, reps in random_patterns:
        # Gerar um timestamp base aleatório
        random_seconds = random.randint(0, int(time_range))
        base_time = min_time + timedelta(seconds=random_seconds)
        
        # Dividir o padrão em partes individuais
        pattern_parts = pattern.split('\n    ')
        
        for _ in range(reps):
            # Para cada parte do padrão, criar um registro
            for part in pattern_parts:
                antecedent, consequent = part.split(' => ')
                # Adicionar pequena variação de tempo entre as partes do padrão
                base_time += timedelta(minutes=random.randint(1, 5))
                new_time = base_time.strftime('%Y-%m-%d %H:%M:%S')
                new_records.append({
                    'timestamp': new_time,
                    'origem': antecedent,
                    'destino': consequent
                })
    
    # Criar DataFrame com os novos registros
    new_df = pd.DataFrame(new_records)
    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])
    
    # Combinar com o original e ordenar por timestamp
    combined_df = pd.concat([df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
    
    # Converter timestamps de volta para string
    combined_df['timestamp'] = combined_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Salvar o novo dataset
    combined_df.to_csv(output_file, index=False)
    total_records = sum(r[1] * pattern_size for r in random_patterns)
    print(f"Dataset com {num_patterns} padrões aleatórios (total {total_records} registros) salvo em '{output_file}'")

    # Salvar os padrões gerados em um arquivo txt
    patterns_file = output_file.replace('.csv', '.txt')
    with open(patterns_file, 'w') as f:
        f.write("Padrões aleatórios gerados:\n\n")
        for i, (pattern, reps) in enumerate(random_patterns, 1):
            f.write(f"{i}. {pattern} - {reps} repetições\n")
    print(f"Lista de padrões salva em '{patterns_file}'")

# Interface com o usuário
if __name__ == "__main__":
    input_csv = input("Digite o nome do arquivo CSV original: ").strip()
    output_csv = input_csv  # Usar o mesmo arquivo para sobrescrever
    
    num_patterns = int(input("Quantos padrões aleatórios deseja gerar? "))
    repetitions = int(input("Quantas repetições para cada padrão? "))
    pattern_size = int(input("Qual o tamanho de cada padrão? "))
    
    generate_random_patterns(input_csv, output_csv, num_patterns, repetitions, pattern_size)