import random
import copy
from collections import defaultdict
from typing import List, Tuple
from domain.cromossomo import Cromossomo
from domain.sala import Sala
from fitness.fitness_evaluator import FitnessEvaluator
from algorithms.grasp import Grasp
import config


def _selecao_torneio(populacao: List[Cromossomo], tamanho_torneio: int = 3) -> Cromossomo:
    torneio = random.sample(populacao, tamanho_torneio)
    return min(torneio, key=lambda ind: ind.fitness)

def _cruzamento(pai1: Cromossomo, pai2: Cromossomo) -> Cromossomo:
    genes_filho = []
    dict_pai1 = defaultdict(list)
    dict_pai2 = defaultdict(list)

    for g in pai1.genes: dict_pai1[f"{g.disciplina.id}_{g.disciplina.turma}"].append(g)
    for g in pai2.genes: dict_pai2[f"{g.disciplina.id}_{g.disciplina.turma}"].append(g)

    for disc_key in dict_pai1.keys():
        if random.random() < 0.5:
            genes_filho.extend(copy.deepcopy(dict_pai1[disc_key]))
        else:
            genes_filho.extend(copy.deepcopy(dict_pai2[disc_key]))

    cromossomo_filho = Cromossomo(genes=genes_filho)
    cromossomo_filho.genes.sort(key=lambda g: f"{g.disciplina.id}_{g.disciplina.turma}")
    return cromossomo_filho

class GeneticAlgorithm:

    def __init__(self, avaliador: FitnessEvaluator, grasp: Grasp, tamanho_populacao: int = 50,
                 geracoes: int = 1000, taxa_mutacao: float = 0.03):
        self.avaliador = avaliador
        self.grasp = grasp
        self.tamanho_populacao = tamanho_populacao
        self.geracoes = geracoes
        self.taxa_mutacao = taxa_mutacao

        self.limite_estagnacao = 20
        self.elitismo_restart = 5
        self.gatilho_busca_local = 0.8
        self.tamanho_elite_busca_local = 3

    def executar(self, salas: List[Sala]) -> Tuple[Cromossomo, List[int]]:
        print(f"\nGerando População Inicial via GRASP ({self.tamanho_populacao} indivíduos).")
        populacao = self.grasp.gerar_populacao_inicial(self.tamanho_populacao)

        for ind in populacao:
            self.avaliador.calcular_fitness(ind)

        melhor_global = min(populacao, key=lambda ind: ind.fitness)
        print(f"Geração 0 -> Fitness: {melhor_global.fitness}")

        historico_fitness = [melhor_global.fitness]
        geracoes_sem_melhoria = 0

        for geracao in range(1, self.geracoes + 1):
            nova_populacao = self._evoluir_populacao(populacao, salas, melhor_global)

            if geracao >= self.geracoes * self.gatilho_busca_local:
                self._aplicar_polimento_elite(nova_populacao)

            populacao = nova_populacao
            melhor_atual = populacao[0]

            if melhor_atual.fitness < melhor_global.fitness:
                melhor_global = copy.deepcopy(melhor_atual)
                geracoes_sem_melhoria = 0
            else:
                geracoes_sem_melhoria += 1

            historico_fitness.append(melhor_global.fitness)

            if geracao % 100 == 0:
                print(f"Geração {geracao} -> Fitness: {melhor_global.fitness}")

            if geracoes_sem_melhoria >= self.limite_estagnacao:
                populacao = self._invocar_terremoto(populacao)
                geracoes_sem_melhoria = 0

            if melhor_global.fitness == 0:
                print("\nSolução perfeita encontrada!")
                break

        return melhor_global, historico_fitness

    def _evoluir_populacao(self, populacao_atual: List[Cromossomo], salas: List[Sala], melhor_global: Cromossomo) -> List[Cromossomo]:
        nova_populacao = [copy.deepcopy(melhor_global)]  # Elitismo Base

        while len(nova_populacao) < self.tamanho_populacao:
            pai1 = _selecao_torneio(populacao_atual)
            pai2 = _selecao_torneio(populacao_atual)

            filho = _cruzamento(pai1, pai2)
            self._mutacao_hibrida(filho, salas)

            self.avaliador.calcular_fitness(filho)
            nova_populacao.append(filho)

        nova_populacao.sort(key=lambda ind: ind.fitness)
        return nova_populacao

    def _mutacao_hibrida(self, cromossomo: Cromossomo, salas: List[Sala]):
        problematicos = getattr(cromossomo, 'disciplinas_problematicas', [])
        top_problematicos = set(problematicos[:10])

        for gene in cromossomo.genes:
            disc_key = f"{gene.disciplina.id}_{gene.disciplina.turma}"
            is_problematico = disc_key in top_problematicos

            chance = self.taxa_mutacao * 5 if is_problematico else self.taxa_mutacao

            if random.random() < chance:
                if random.random() < 0.5:
                    if gene.disciplina.turno == "MATUTINO":
                        horarios_permitidos = config.TURNO_MATUTINO
                    elif gene.disciplina.turno == "VESPERTINO":
                        horarios_permitidos = config.TURNO_VESPERTINO
                    elif gene.disciplina.turno == "NOTURNO":
                        horarios_permitidos = config.TURNO_NOTURNO
                    else:
                        horarios_permitidos = config.HORARIOS_DISPONIVEIS

                    gene.horario = random.choice(horarios_permitidos)
                else:
                    salas_compativeis = [s for s in salas if s.is_lab == gene.disciplina.lab]
                    if salas_compativeis:
                        gene.sala = random.choice(salas_compativeis)

    def _aplicar_polimento_elite(self, populacao: List[Cromossomo]) -> None:
        for i in range(min(self.tamanho_elite_busca_local, len(populacao))):
            self._busca_local(populacao[i])

    def _busca_local(self, cromossomo: Cromossomo, max_tentativas: int = 10) -> None:
        melhor_fitness = cromossomo.fitness

        for _ in range(max_tentativas):
            idx1 = random.randint(0, len(cromossomo.genes) - 1)
            idx2 = random.randint(0, len(cromossomo.genes) - 1)

            if idx1 == idx2: continue

            gene1 = cromossomo.genes[idx1]
            gene2 = cromossomo.genes[idx2]

            if gene1.disciplina.turno == gene2.disciplina.turno and gene1.disciplina.lab == gene2.disciplina.lab:

                gene1.horario, gene2.horario = gene2.horario, gene1.horario
                gene1.sala, gene2.sala = gene2.sala, gene1.sala

                novo_fitness = self.avaliador.calcular_fitness(cromossomo)

                if novo_fitness < melhor_fitness:
                    melhor_fitness = novo_fitness
                else:
                    gene1.horario, gene2.horario = gene2.horario, gene1.horario
                    gene1.sala, gene2.sala = gene2.sala, gene1.sala
                    cromossomo.fitness = melhor_fitness

    def _invocar_terremoto(self, populacao: List[Cromossomo]) -> List[Cromossomo]:
        print(f"Estagnação detectada. Invocando o Terremoto...")
        populacao.sort(key=lambda ind: ind.fitness)

        nova_populacao_restart = [copy.deepcopy(ind) for ind in populacao[:self.elitismo_restart]]

        num_novos = self.tamanho_populacao - self.elitismo_restart
        novos_individuos = self.grasp.gerar_populacao_inicial(num_novos)

        for ind in novos_individuos:
            self.avaliador.calcular_fitness(ind)

        nova_populacao_restart.extend(novos_individuos)
        return nova_populacao_restart