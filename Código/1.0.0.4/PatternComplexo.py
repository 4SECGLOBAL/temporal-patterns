import pandas as pd
import random
from datetime import datetime, timedelta

def generate_random_patterns(input_csv, output_csv, num_patterns, repetitions, pattern_size, max_time_between_parts):
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_csv}' não encontrado.")
        return
    
    random_patterns = []
    pattern_tracking = []  
    
    for _ in range(num_patterns):
        pattern_sequence = []
        for _ in range(pattern_size):
            antecedent = random.randint(100, 9999)
            consequent = random.randint(100, 9999)
            pattern_sequence.append(f"{antecedent} => {consequent}")
        pattern_str = "\n".join(pattern_sequence)
        random_patterns.append((pattern_str, repetitions))
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    min_time = df['timestamp'].min()
    max_time = df['timestamp'].max()
    time_range = (max_time - min_time).total_seconds()
    
    new_records = []
    for pattern, reps in random_patterns:
        pattern_parts = pattern.split('\n')
        
        for rep in range(reps):
            random_seconds = random.randint(0, int(time_range))
            base_time = min_time + timedelta(seconds=random_seconds)
            rep_timestamps = []
            
            for part in pattern_parts:
                antecedent, consequent = part.split(' => ')

                new_time = base_time.strftime('%Y-%m-%d %H:%M:%S')
                new_records.append({
                    'timestamp': new_time,
                    'origem': antecedent,
                    'destino': consequent
                })
                
                rep_timestamps.append(new_time)
                
                if part != pattern_parts[-1]:
                    time_increment = random.randint(int(max_time_between_parts/4), max_time_between_parts)
                    base_time += timedelta(seconds=time_increment)
            
            pattern_tracking.append({
                'pattern': pattern,
                'repetition': rep + 1,
                'timestamps': rep_timestamps
            })
    
    new_df = pd.DataFrame(new_records)
    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], format='%Y-%m-%d %H:%M:%S')
    
    combined_df = pd.concat([df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
    
    combined_df['timestamp'] = combined_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    combined_df.to_csv(output_csv, index=False)
    
    # Salvar .txt
    patterns_file = output_csv.replace('.csv', '.txt')
    with open(patterns_file, 'w') as f:
        f.write("Padrões inseridos e seus timestamps:\n\n")
        for i, track in enumerate(pattern_tracking, 1):
            f.write(f"=== Acontecimento {i} ===\n")
            f.write(f"Conteúdo:\n{track['pattern']}\n")
            f.write(f"Repetição: {track['repetition']}\n")
            f.write("Timestamps de inserção:\n")
            
            parts = track['pattern'].strip().split('\n')
            for j, (part, ts) in enumerate(zip(parts, track['timestamps'])):
                cleaned_part = part.strip()
                f.write(f"  Parte {j+1}: {ts} | {cleaned_part}\n")
            f.write("\n")
    
def insert_defined_patterns(input_csv, output_txt, patterns_list, max_time_between_parts):
    
    output_csv = input_csv
    
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_csv}' não encontrado.")
        return
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    min_time = df['timestamp'].min()
    max_time = df['timestamp'].max()
    time_range = (max_time - min_time).total_seconds()
    
    new_records = []
    pattern_tracking = []
    
    for pattern_info in patterns_list:
        pattern = pattern_info['pattern']
        reps = pattern_info['repetitions']
        pattern_parts = [p.strip() for p in pattern.split('\n') if p.strip()]
        
        for rep in range(reps):
            random_seconds = random.randint(0, int(time_range))
            base_time = min_time + timedelta(seconds=random_seconds)
            rep_timestamps = []
            
            
            # Tarefa I: Rastrear cada padrão para salvar
            for part in pattern_parts:
                try:
                    if '=>' not in part:
                        continue
                        
                    antecedent, consequent = [x.strip() for x in part.split('=>', 1)]
                    
                    new_time = base_time.strftime('%Y-%m-%d %H:%M:%S')
                    new_records.append({
                        'timestamp': new_time,
                        'origem': antecedent,
                        'destino': consequent
                    })
                    
                    rep_timestamps.append(new_time)
                    
                    if part != pattern_parts[-1]:
                        time_increment = random.randint(int(max_time_between_parts/4), max_time_between_parts)
                        base_time += timedelta(seconds=time_increment)
                        
                except ValueError as e:
                    print(f"Erro ao processar: '{part}'. Erro: {e}")
                    continue
            
            # Tarefa II: pegar os timestamps 
            pattern_tracking.append({
                'pattern': pattern,
                'repetition': rep + 1,
                'timestamps': rep_timestamps
            })
    
    new_df = pd.DataFrame(new_records)
    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])
    
    combined_df = pd.concat([df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
    
    combined_df['timestamp'] = combined_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    combined_df.to_csv(output_csv, index=False)
    
    
    # Tarefa III: Salvar os padrões inseridos em um arquivo txt
    patterns_file = output_txt
    with open(patterns_file, 'w') as f:
        f.write("Padrões inseridos e seus timestamps:\n\n")
        for i, track in enumerate(pattern_tracking, 1):
            f.write(f"=== Acontecimento {i} ===\n")
            f.write(f"Conteúdo:\n{track['pattern']}\n")
            f.write(f"Repetição: {track['repetition']}\n")
            f.write("Timestamps de inserção:\n")
            
            parts = track['pattern'].strip().split('\n')
            for j, (part, ts) in enumerate(zip(parts, track['timestamps'])):
                cleaned_part = part.strip()
                f.write(f"  Parte {j+1}: {ts} | {cleaned_part}\n")
            f.write("\n")
    
#     print(f"Dataset salvo em '{output_csv}'")
#     print(f"Relatório salvo em '{patterns_file}'")


if __name__ == "__main__":
    input_csv = input("Digite o nome do arquivo CSV original: ").strip()
    output_csv = input_csv  # Usar o mesmo arquivo para sobrescrever
    
    num_patterns = int(input("Quantos padrões aleatórios deseja gerar? "))
    repetitions = int(input("Quantas repetições para cada padrão? "))
    pattern_size = int(input("Qual o tamanho de cada padrão? "))
    max_time_between_parts = int(input("Tempo máximo (minutos) entre partes do padrão: "))
    
    generate_random_patterns(input_csv, output_csv, num_patterns, repetitions, pattern_size, max_time_between_parts)
    insert_defined_patterns(input_csv, output_csv, patterns, max_time_between_parts)