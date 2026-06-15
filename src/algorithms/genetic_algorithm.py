import random
import copy
from typing import List
from domain.cromossomo import Cromossomo
from domain.sala import Sala
from fitness.fitness_evaluator import FitnessEvaluator
from algorithms.grasp import Grasp
import config


class GeneticAlgorithm:

    def __init__(self, avaliador: FitnessEvaluator, grasp: Grasp, tamanho_populacao: int = 50, geracoes: int = 100,
                 taxa_mutacao: float = 0.1):
        self.avaliador = avaliador
        self.grasp = grasp
        self.tamanho_populacao = tamanho_populacao
        self.geracoes = geracoes
        self.taxa_mutacao = taxa_mutacao

    def _selecao_torneio(self, populacao: List[Cromossomo], tamanho_torneio: int = 3) -> Cromossomo:
        torneio = random.sample(populacao, tamanho_torneio)
        return min(torneio, key=lambda ind: ind.fitness)

    def _cruzamento(self, pai1: Cromossomo, pai2: Cromossomo) -> Cromossomo:
        ponto_corte = random.randint(1, len(pai1.genes) - 1)
        genes_filho = copy.deepcopy(pai1.genes[:ponto_corte]) + copy.deepcopy(pai2.genes[ponto_corte:])
        return Cromossomo(genes=genes_filho)

    def _mutacao(self, cromossomo: Cromossomo, salas: List[Sala]):
        for gene in cromossomo.genes:
            if random.random() < self.taxa_mutacao:
                if random.random() < 0.5:
                    # MUTAÇÃO DE HORÁRIO INTELIGENTE
                    horarios_permitidos = config.TURNOS_NOITE if gene.disciplina.turno_curso == "NOITE" else config.HORARIOS_DISPONIVEIS
                    gene.horario = random.choice(horarios_permitidos)
                else:
                    if gene.disciplina.instituto != "IC":
                        continue

                    salas_compativeis = [s for s in salas if
                                         s.is_lab == gene.disciplina.needs_lab and s.id != "EXTERNA"]
                    if salas_compativeis:
                        gene.sala = random.choice(salas_compativeis)

    def executar(self, salas: List[Sala]) -> tuple[Cromossomo, List[int]]:
        print(f"\nA gerar População Inicial via GRASP ({self.tamanho_populacao} indivíduos)...")
        populacao = self.grasp.gerar_populacao_inicial(self.tamanho_populacao)

        for ind in populacao:
            self.avaliador.calcular_fitness(ind)

        melhor_global = min(populacao, key=lambda ind: ind.fitness)
        print(f"Melhor Fitness Inicial (Geração 0): {melhor_global.fitness}")

        historico_fitness = [melhor_global.fitness]

        for geracao in range(1, self.geracoes + 1):
            nova_populacao = []
            nova_populacao.append(copy.deepcopy(melhor_global))

            while len(nova_populacao) < self.tamanho_populacao:
                pai1 = self._selecao_torneio(populacao)
                pai2 = self._selecao_torneio(populacao)

                filho = self._cruzamento(pai1, pai2)
                self._mutacao(filho, salas)

                self.avaliador.calcular_fitness(filho)
                nova_populacao.append(filho)

            populacao = nova_populacao
            melhor_atual = min(populacao, key=lambda ind: ind.fitness)

            if melhor_atual.fitness < melhor_global.fitness:
                melhor_global = copy.deepcopy(melhor_atual)

            print(f"Geração {geracao} | Melhor Fitness: {melhor_global.fitness}")
            historico_fitness.append(melhor_global.fitness)

            if melhor_global.fitness == 0:
                print("\nSolução perfeita encontrada! A interromper evolução.")
                break

        return melhor_global, historico_fitness