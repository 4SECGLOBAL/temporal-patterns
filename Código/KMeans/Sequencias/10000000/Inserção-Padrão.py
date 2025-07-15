import pandas as pd
import random
from datetime import datetime, timedelta

def generate_random_patterns(input_file, output_file, num_patterns, repetitions):
    # Carregar o dataset original
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        return
    
    # Gerar padrões aleatórios
    random_patterns = []
    for _ in range(num_patterns):
        antecedent = random.randint(1000, 9999)
        consequent = random.randint(1000, 9999)
        pattern = f"{antecedent} => {consequent}"
        random_patterns.append((pattern, repetitions))
    
    # Gerar timestamps sequenciais
    start_time = datetime.strptime(df['timestamp'].max(), '%Y-%m-%d %H:%M:%S') + timedelta(minutes=1)
    
    # Criar novos registros com os padrões aleatórios
    new_records = []
    for pattern, reps in random_patterns:
        antecedent, consequent = pattern.split(' => ')
        for _ in range(reps):
            new_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
            new_records.append({
                'timestamp': new_time,
                'origem': antecedent,
                'destino': consequent
            })
            start_time += timedelta(minutes=random.randint(1, 10))
    
    # Adicionar ao dataframe original
    new_df = pd.concat([df, pd.DataFrame(new_records)], ignore_index=True)
    
    # Salvar o novo dataset
    new_df.to_csv(output_file, index=False)
    print(f"Dataset com {num_patterns} padrões aleatórios (total {sum(r[1] for r in random_patterns)} registros) salvo em '{output_file}'")

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
    output_csv = input("Digite o nome do arquivo CSV de saída: ").strip()
    
    num_patterns = int(input("Quantos padrões aleatórios deseja gerar? "))
    repetitions = int(input("Quantas repetições para cada padrão? "))
    
    generate_random_patterns(input_csv, output_csv, num_patterns, repetitions)