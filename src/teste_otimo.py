import time
import csv
from pathlib import Path
from typing import List

from infrastructure.data_loader import DataLoader
from fitness.fitness_evaluator import FitnessEvaluator
from algorithms.grasp import Grasp
from algorithms.genetic_algorithm import GeneticAlgorithm


def _criar_diretorio_resultados() -> Path:
    dir_raiz = Path(__file__).resolve().parent.parent
    dir_resultados = dir_raiz / "resultados_otimos"
    dir_resultados.mkdir(parents=True, exist_ok=True)
    return dir_resultados


def _salvar_historico_consolidado(caminho_arquivo: Path, matriz_historico: List[List[float]], total_runs: int):
    with open(caminho_arquivo, mode='w', encoding='utf-8', newline='') as f:
        escritor = csv.writer(f, delimiter=';')

        cabecalho = ["Geracao"] + [f"Iteracao_{i}" for i in range(1, total_runs + 1)]
        escritor.writerow(cabecalho)

        for geracao, fitness_runs in enumerate(matriz_historico):
            linha = [geracao] + fitness_runs
            escritor.writerow(linha)


def main():
    print("\nIniciando bateria de testes ótimos\n")

    loader = DataLoader('data/')
    professores = loader.carregar_professores()
    salas = loader.carregar_salas()
    disciplinas = loader.carregar_disciplinas()

    avaliador = FitnessEvaluator(professores)
    grasp = Grasp(professores, salas, disciplinas)

    geracoes_totais = 500
    total_runs = 30

    populacao_otima = 30
    mutacao_otima = 0.0094

    matriz_historico = [[] for _ in range(geracoes_totais)]

    for run in range(1, total_runs + 1):
        print(f">>> Rodando Iteração {run}/{total_runs} (Pop={populacao_otima}, Mutação={mutacao_otima})")

        ag = GeneticAlgorithm(
            avaliador=avaliador,
            grasp=grasp,
            tamanho_populacao=populacao_otima,
            geracoes=geracoes_totais,
            taxa_mutacao=mutacao_otima
        )

        inicio = time.time()
        melhor_solucao, historico = ag.executar(salas)
        fim = time.time()

        for geracao, valor_fitness in enumerate(historico):
            if geracao < geracoes_totais:
                matriz_historico[geracao].append(valor_fitness)

        print(f"    Concluído em {(fim - inicio):.2f}s | Melhor Fitness Alcançado: {melhor_solucao.fitness}")

    dir_resultados = _criar_diretorio_resultados()
    arquivo_saida = dir_resultados / "historico_runs_otimas.csv"

    _salvar_historico_consolidado(arquivo_saida, matriz_historico, total_runs)
    print(f"Arquivo gerado em: {arquivo_saida}")


if __name__ == "__main__":
    main()