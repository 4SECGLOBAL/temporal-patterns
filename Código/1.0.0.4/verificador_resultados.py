import os

def verificar_resultados():

    # Tarefa I. pegar os arquivos de resultado
    arquivos = [f for f in os.listdir() if f.startswith("Resultado_") and f.endswith(".txt")]

    falhas_encontradas = False
    resultado_negativo = []

    for arquivo in arquivos:
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

            teste_atual = None
            falha_no_arquivo = False
            falhas_do_arquivo = []

            for linha in linhas:
                # Tarefa II. verificar o número de teste
                if linha.startswith("=== Análise detalhada para teste"):
                    # II. 1. encontra o número do teste
                    teste_atual = linha.split("teste ")[1].split(" ===")[0].strip()

                # Tarefa III. verificar se a linha encontra falha
                elif "Todos os padrões foram encontrados? Não" in linha:
                    falhas_encontradas = True
                    falha_no_arquivo = True
                    falhas_do_arquivo.append(teste_atual)


            if falha_no_arquivo:
                mensagem = f"Arquivo: {arquivo}\nTestes que falharam: {', '.join(falhas_do_arquivo)}\n"
                resultado_negativo.append(mensagem)

    if resultado_negativo:
        with open('resultados_negativos.txt', 'w', encoding='utf-8') as f:
            f.write("=== RESULTADOS NEGATIVOS ENCONTRADOS ===\n\n")
            f.write("\n".join(resultado_negativo))
            f.write(f"\nTotal de arquivos com falhas: {len(resultado_negativo)}")

    if not falhas_encontradas:
        print("Nenhuma falha encontrada em todos os arquivos analisados.")
        # criar apenas um arquivo vazio para mostrar que não tem nenhuma falha
        with open('resultados_negativos.txt', 'w', encoding='utf-8') as f:
            f.write("Nenhuma falha encontrada em todos os arquivos analisados.")

if __name__ == "__main__":
    verificar_resultados()