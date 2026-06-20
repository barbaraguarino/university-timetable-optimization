import time
import csv
import statistics
from pathlib import Path
from infrastructure.data_loader import DataLoader
from fitness.fitness_evaluator import FitnessEvaluator
from algorithms.grasp import Grasp
from algorithms.genetic_algorithm import GeneticAlgorithm


def _criar_diretorio_resultados() -> Path:
    dir_raiz = Path(__file__).resolve().parent.parent
    dir_resultados = dir_raiz / "resultados_teste"
    dir_resultados.mkdir(parents=True, exist_ok=True)
    return dir_resultados


def main():
    print("\nIniciando bateria de testes (30 Runs)\n")

    loader = DataLoader('data/')
    professores = loader.carregar_professores()
    salas = loader.carregar_salas()
    disciplinas = loader.carregar_disciplinas()

    avaliador = FitnessEvaluator(professores)
    grasp = Grasp(professores, salas, disciplinas)

    geracoes_teste = 500
    runs_por_experimento = 30

    experimentos = [
        {"id": 1, "pop": 30, "mutacao": 0.0094},
        {"id": 2, "pop": 30, "mutacao": 0.0189},
        {"id": 3, "pop": 30, "mutacao": 0.0377},
        {"id": 4, "pop": 40, "mutacao": 0.0094},
        {"id": 5, "pop": 60, "mutacao": 0.0094},
        {"id": 6, "pop": 100, "mutacao": 0.0566},
    ]

    dir_resultados = _criar_diretorio_resultados()
    arq_estatisticas = dir_resultados / "tabela_estatisticas.csv"

    with open(arq_estatisticas, mode='w', encoding='utf-8', newline='') as f:
        escritor = csv.writer(f, delimiter=';')  # Ponto e vírgula facilita importar no Excel/Sheets pt-BR
        escritor.writerow(["Experimento_ID", "Tamanho_Pop", "Taxa_Mutacao", "Tempo_Medio(s)",
                           "Fitness_Medio", "Fitness_Melhor", "Fitness_Pior", "Desvio_Padrao"])

    print(f"Serão testadas {len(experimentos)} configurações, rodando {runs_por_experimento} vezes cada.\n")

    for exp in experimentos:
        print(f">>> Rodando Experimento {exp['id']} (Pop={exp['pop']}, Mutacao={exp['mutacao']})")

        fitness_list = []
        tempos_list = []
        melhor_historico_do_exp = None
        melhor_fitness_do_exp = float('inf')

        for run in range(1, runs_por_experimento + 1):
            ag = GeneticAlgorithm(
                avaliador=avaliador,
                grasp=grasp,
                tamanho_populacao=exp['pop'],
                geracoes=geracoes_teste,
                taxa_mutacao=exp['mutacao']
            )

            inicio = time.time()
            melhor_solucao, historico = ag.executar(salas)
            fim = time.time()

            tempo_exec = fim - inicio
            fit = melhor_solucao.fitness

            tempos_list.append(tempo_exec)
            fitness_list.append(fit)

            if fit < melhor_fitness_do_exp:
                melhor_fitness_do_exp = fit
                melhor_historico_do_exp = historico

            print(f"    Run {run}/{runs_por_experimento} | Fitness: {fit} | Tempo: {tempo_exec:.2f}s")

        tempo_medio = statistics.mean(tempos_list)
        fitness_medio = statistics.mean(fitness_list)
        fitness_melhor = min(fitness_list)
        fitness_pior = max(fitness_list)
        desvio_padrao = statistics.stdev(fitness_list) if runs_por_experimento > 1 else 0.0

        # Escrever na tabela geral
        with open(arq_estatisticas, mode='a', encoding='utf-8', newline='') as f:
            escritor = csv.writer(f, delimiter=';')
            escritor.writerow([
                exp['id'], exp['pop'], exp['mutacao'],
                round(tempo_medio, 2), round(fitness_medio, 2),
                fitness_melhor, fitness_pior, round(desvio_padrao, 2)
            ])

        arq_historico = dir_resultados / f"historico_convergencia_exp{exp['id']}.csv"
        with open(arq_historico, mode='w', encoding='utf-8', newline='') as f:
            escritor = csv.writer(f, delimiter=';')
            escritor.writerow(["Geracao", "Melhor_Fitness"])
            for geracao, valor_fit in enumerate(melhor_historico_do_exp):
                escritor.writerow([geracao, valor_fit])

        print(
            f"Resumo Exp {exp['id']}: Fit Medio = {fitness_medio:.2f} | Melhor = {fitness_melhor} | Tempo Medio = {tempo_medio:.2f}s\n")

    print(f"Todos os testes concluídos.")
    print(f"Os arquivos .csv foram salvos na pasta: {dir_resultados}")


if __name__ == "__main__":
    main()