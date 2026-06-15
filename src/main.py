import csv
from infrastructure.data_loader import DataLoader
from fitness.fitness_evaluator import FitnessEvaluator
from algorithms.grasp import Grasp
from algorithms.genetic_algorithm import GeneticAlgorithm


def main():
    print("Otimização de Quadro de Horários Universitário (UCTP)\n")

    loader = DataLoader()
    professores = loader.carregar_professores()
    salas = loader.carregar_salas()
    disciplinas = loader.carregar_disciplinas()

    print(f"Dados carregados: {len(professores)} Docentes | {len(salas)} Salas | {len(disciplinas)} Disciplinas")

    avaliador = FitnessEvaluator(professores)
    grasp = Grasp(professores, salas, disciplinas)

    ag = GeneticAlgorithm(
        avaliador=avaliador,
        grasp=grasp,
        tamanho_populacao=50,
        geracoes=100,
        taxa_mutacao=0.1
    )

    print("\nA iniciar Algoritmo Genético Híbrido...")
    melhor_solucao, historico = ag.executar(salas)

    caminho_resultados = loader.data_folder.parent / 'resultados.csv'
    with open(caminho_resultados, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Geracao', 'Melhor_Fitness'])
        for i, valor_fitness in enumerate(historico):
            writer.writerow([i, valor_fitness])

    print(f"\nFicheiro de resultados exportado com sucesso para: {caminho_resultados.name}")

    print("\n=========================================")
    print("RESULTADO FINAL OTIMIZADO")
    print("=========================================")
    print(f"Nota de Penalidade (Fitness): {melhor_solucao.fitness} pontos")

    print("\nGrelha de Horários Gerada:")
    genes_ordenados = sorted(melhor_solucao.genes, key=lambda g: g.horario)
    for gene in genes_ordenados:
        print(f"[{gene.horario}] {gene.disciplina.nome} (Prof: {gene.disciplina.id_professor}) -> Sala: {gene.sala.id}")


if __name__ == '__main__':
    main()