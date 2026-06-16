import time
import os
from infrastructure.data_loader import DataLoader
from fitness.fitness_evaluator import FitnessEvaluator
from algorithms.grasp import Grasp
from algorithms.genetic_algorithm import GeneticAlgorithm


def main():
    print("Otimização de Quadro de Horários Universitário (UCTP)\n")

    DIRETORIO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    loader = DataLoader('data/')

    professores = loader.carregar_professores()
    salas = loader.carregar_salas()
    disciplinas = loader.carregar_disciplinas()

    print(f"Dados carregados: {len(professores)} Docentes | {len(salas)} Salas | {len(disciplinas)} Disciplinas\n")

    avaliador = FitnessEvaluator(professores)
    grasp = Grasp(professores, salas, disciplinas)

    ag = GeneticAlgorithm(
        avaliador=avaliador,
        grasp=grasp,
        tamanho_populacao=50,
        geracoes=2000,
        taxa_mutacao=0.01
    )

    print("A iniciar Algoritmo Memético (GRASP + Genético + Busca Local)...")
    start_time = time.time()
    melhor_solucao, historico = ag.executar(salas)
    end_time = time.time()

    dias_ordem = {"Segunda": 1, "Terca": 2, "Quarta": 3, "Quinta": 4, "Sexta": 5}
    genes_ordenados = sorted(
        melhor_solucao.genes,
        key=lambda g: (dias_ordem.get(g.horario.split('_')[0], 99), g.horario.split('_')[1])
    )

    nome_arquivo = os.path.join(DIRETORIO_RAIZ, "grade_de_horarios_final.csv")

    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("Codigo_Disciplina,Nome_Disciplina,Professor,Sala,Horario\n")

        for gene in genes_ordenados:
            prof = professores.get(gene.disciplina.id_professor)
            nome_professor = prof.nome if prof else gene.disciplina.id_professor

            f.write(f"{gene.disciplina.id},{gene.disciplina.nome},{nome_professor},{gene.sala.id},{gene.horario}\n")

    print(f"\nFicheiro de resultados exportado com sucesso para a raiz: {nome_arquivo}")
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")

    print("\n=========================================")
    print("RESULTADO FINAL OTIMIZADO")
    print("=========================================")
    print(f"Nota de Penalidade (Fitness): {melhor_solucao.fitness} pontos\n")

    print("Grelha de Horários Gerada:")
    for gene in genes_ordenados:
        prof = professores.get(gene.disciplina.id_professor)
        nome_professor = prof.nome if prof else gene.disciplina.id_professor
        print(f"[{gene.horario}] {gene.disciplina.nome} (Prof: {nome_professor}) -> Sala: {gene.sala.id}")


if __name__ == "__main__":
    main()