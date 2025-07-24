import pandas as pd
import random
from datetime import datetime, timedelta
import string

def generate_random_letters(length=4):

    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


def generate_random_patterns(input_file, output_file, num_patterns, repetitions, pattern_size, max_time_between_parts):
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        return
    
    random_patterns = []
    for _ in range(num_patterns):
        pattern_sequence = []
        for _ in range(pattern_size):
            antecedent = generate_random_letters()
            consequent = generate_random_letters()
            pattern_sequence.append(f"{antecedent} => {consequent}")
        random_patterns.append(("\n    ".join(pattern_sequence), repetitions))
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    min_time = df['timestamp'].min()
    max_time = df['timestamp'].max()
    time_range = (max_time - min_time).total_seconds()
    
    new_records = []
    for pattern, reps in random_patterns:
        # Dividir o padrão em partes individuais
        pattern_parts = pattern.split('\n    ')
        
        for rep in range(reps):

            random_seconds = random.randint(0, int(time_range))
            base_time = min_time + timedelta(seconds=random_seconds)
            
            # Criar um registro para cada repetição
            for part in pattern_parts:
                antecedent, consequent = part.split(' => ')

                new_time = base_time.strftime('%Y-%m-%d %H:%M:%S')
                new_records.append({
                    'timestamp': new_time,
                    'origem': antecedent,
                    'destino': consequent
                })

                if part != pattern_parts[-1]:
                    time_increment = random.randint(1, max_time_between_parts)
                    base_time += timedelta(minutes=time_increment)
    

    new_df = pd.DataFrame(new_records)
    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])
    
    combined_df = pd.concat([df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
    
    combined_df['timestamp'] = combined_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
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

if __name__ == "__main__":
    input_csv = input("Digite o nome do arquivo CSV original: ").strip()
    output_csv = input_csv  # Usar o mesmo arquivo para sobrescrever
    
    num_patterns = int(input("Quantos padrões aleatórios deseja gerar? "))
    repetitions = int(input("Quantas repetições para cada padrão? "))
    pattern_size = int(input("Qual o tamanho de cada padrão? "))
    max_time_between_parts = int(input("Tempo máximo (minutos) entre partes do padrão: "))
    
    generate_random_patterns(input_csv, output_csv, num_patterns, repetitions, pattern_size, max_time_between_parts)