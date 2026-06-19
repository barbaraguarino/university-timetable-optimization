import time
import csv
from pathlib import Path
from infrastructure.data_loader import DataLoader
from fitness.fitness_evaluator import FitnessEvaluator
from algorithms.grasp import Grasp
from algorithms.genetic_algorithm import GeneticAlgorithm
from domain.cromossomo import Cromossomo
import config


def _criar_diretorio_resultados() -> Path:
    dir_raiz = Path(__file__).resolve().parent.parent
    dir_resultados = dir_raiz / "resultados"

    dir_resultados.mkdir(parents=True, exist_ok=True)
    return dir_resultados

def _salvar_grade_horarios(cromossomo: Cromossomo, professores: dict, caminho_arquivo: Path) -> None:
    genes_ordenados = sorted(
        cromossomo.genes,
        key=lambda g: g.horario
    )

    with open(caminho_arquivo, mode='w', encoding='utf-8', newline='') as f:
        escritor = csv.writer(f)
        escritor.writerow(["Código", "Disciplina", "Turma", "Professor", "Sala", "Horário"])

        for gene in genes_ordenados:
            prof = professores.get(gene.disciplina.id_professor)
            nome_professor = prof.nome if prof else gene.disciplina.id_professor

            escritor.writerow([
                gene.disciplina.id,
                gene.disciplina.nome,
                gene.disciplina.turma,
                nome_professor,
                gene.sala.id,
                config.id_to_str(gene.horario)
            ])

def _salvar_historico_fitness(historico: list, caminho_arquivo: Path) -> None:
    with open(caminho_arquivo, mode='w', encoding='utf-8', newline='') as f:
        escritor = csv.writer(f)
        escritor.writerow(["Geracao", "Fitness"])

        for geracao, fitness in enumerate(historico):
            escritor.writerow([geracao, fitness])

def _salvar_extrato_penalidades(avaliador: FitnessEvaluator, cromossomo: Cromossomo, caminho_arquivo: Path) -> None:
    extrato = avaliador.auditar_solucao(cromossomo)

    with open(caminho_arquivo, mode='w', encoding='utf-8', newline='') as f:
        escritor = csv.DictWriter(f, fieldnames=["Tipo", "Regra", "Disciplina", "Detalhe", "Pontos"])
        escritor.writeheader()
        for linha in extrato:
            escritor.writerow(linha)

def main():
    print("\nOtimização de Quadro de Horários Universitário (UCTP)\n")

    loader = DataLoader('data/')
    professores = loader.carregar_professores()
    salas = loader.carregar_salas()
    disciplinas = loader.carregar_disciplinas()

    print(f"Dados carregados: {len(professores)} Docentes | {len(salas)} Salas | {len(disciplinas)} Disciplinas \n")

    avaliador = FitnessEvaluator(professores)
    grasp = Grasp(professores, salas, disciplinas)

    ag = GeneticAlgorithm(
        avaliador=avaliador,
        grasp=grasp,
        tamanho_populacao=50,
        geracoes=2000,
        taxa_mutacao=0.01
    )

    print("Iniciando Algoritmo GRASP + Genético + Busca Local")
    start_time = time.time()
    melhor_solucao, historico = ag.executar(salas)
    end_time = time.time()

    dir_resultados = _criar_diretorio_resultados()
    arq_grade = dir_resultados / "grade_final.csv"
    arq_historico = dir_resultados / "historico_geracoes.csv"
    arq_extrato = dir_resultados / "extrato_multas.csv"

    try:
        _salvar_grade_horarios(melhor_solucao, professores, arq_grade)
        _salvar_historico_fitness(historico, arq_historico)
        _salvar_extrato_penalidades(avaliador, melhor_solucao, arq_extrato)
    except PermissionError:
        print("\nERRO: Feche os arquivos CSV que estão abertos e rode novamente para salvar!")
        return

    print("\nRESULTADO FINAL OTIMIZADO")
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")
    print(f"Nota de Penalidade (Fitness): {melhor_solucao.fitness} pontos")
    print(f"Grade salva em: {arq_grade.relative_to(dir_resultados.parent)}")
    print(f"Histórico salvo em: {arq_historico.relative_to(dir_resultados.parent)}")
    print(f"Extrato de multas salvo em: {arq_extrato.relative_to(dir_resultados.parent)}")


if __name__ == "__main__":
    main()