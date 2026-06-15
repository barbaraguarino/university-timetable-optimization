from collections import defaultdict
from typing import Dict, List
from domain.cromossomo import Cromossomo
from domain.professor import Professor
import config

class FitnessEvaluator:

    def __init__(self, professores: Dict[str, Professor]):
        self.professores = professores

    def calcular_fitness(self, cromossomo: Cromossomo) -> int:
        penalidade_total = 0

        alocacoes_por_horario = defaultdict(list)
        alocacoes_por_docente_dia = defaultdict(list)
        alocacoes_por_periodo_dia = defaultdict(list)

        for gene in cromossomo.genes:
            alocacoes_por_horario[gene.horario].append(gene)
            dia = gene.horario.split("_")[0]
            alocacoes_por_docente_dia[(gene.disciplina.id_professor, dia)].append(gene)
            alocacoes_por_periodo_dia[(gene.disciplina.periodo, dia)].append(gene)

        penalidade_total += self._avaliar_hc_por_horario(alocacoes_por_horario)
        penalidade_total += self._avaliar_hc_disponibilidade(cromossomo.genes)
        penalidade_total += self._avaliar_hc_novas_regras(cromossomo.genes)

        penalidade_total += self._avaliar_sc_distribuicao_semanal(cromossomo.genes)
        penalidade_total += self._avaliar_sc_infraestrutura(cromossomo.genes)
        penalidade_total += self._avaliar_sc_pedagogia(cromossomo.genes)
        penalidade_total += self._avaliar_sc_jornada_docente(alocacoes_por_docente_dia)
        penalidade_total += self._avaliar_sc_jornada_aluno(alocacoes_por_periodo_dia)
        penalidade_total += self._avaliar_sc_equidade(cromossomo.genes)

        cromossomo.fitness = penalidade_total
        return penalidade_total

    def _avaliar_hc_por_horario(self, alocacoes_por_horario: dict) -> int:
        penalidade = 0
        for horario, genes in alocacoes_por_horario.items():
            professores_vistos = set()
            salas_vistas = set()
            periodos_vistos = set()

            if horario in config.HORARIOS_PROIBIDOS:
                penalidade += config.PESO_HARD * len(genes)

            for gene in genes:
                if gene.disciplina.id_professor != "EXT":
                    if gene.disciplina.id_professor in professores_vistos:
                        penalidade += config.PESO_HARD
                    professores_vistos.add(gene.disciplina.id_professor)

                if gene.sala.id != "EXTERNA":
                    if gene.sala.id in salas_vistas:
                        penalidade += config.PESO_HARD
                    salas_vistas.add(gene.sala.id)

                chave_periodo = (gene.disciplina.periodo, gene.disciplina.turno_curso)
                if chave_periodo in periodos_vistos:
                    penalidade += config.PESO_HARD
                periodos_vistos.add(chave_periodo)

        return penalidade

    def _avaliar_hc_disponibilidade(self, genes: List) -> int:
        penalidade = 0
        for gene in genes:
            if gene.disciplina.id_professor != "EXT":
                prof = self.professores.get(gene.disciplina.id_professor)
                if prof and not prof.is_disponivel(gene.horario):
                    penalidade += config.PESO_HARD
        return penalidade

    def _avaliar_hc_novas_regras(self, genes: List) -> int:
        penalidade = 0
        for gene in genes:
            if gene.disciplina.instituto == "IC":
                if gene.disciplina.needs_lab != gene.sala.is_lab:
                    penalidade += config.PESO_HARD

            if gene.disciplina.turno_curso == "NOITE" and gene.horario not in config.TURNOS_NOITE:
                penalidade += config.PESO_HARD
        return penalidade

    def _avaliar_sc_distribuicao_semanal(self, genes: List) -> int:
        penalidade = 0
        alocacoes_por_disciplina = defaultdict(list)

        for gene in genes:
            alocacoes_por_disciplina[gene.disciplina.id].append(gene)

        for id_disc, genes_da_disc in alocacoes_por_disciplina.items():
            if len(genes_da_disc) > 1:
                dias = [config.DIAS_DA_SEMANA[g.horario.split("_")[0]] for g in genes_da_disc]
                dias.sort()

                for i in range(len(dias) - 1):
                    distancia = dias[i + 1] - dias[i]
                    if distancia == 0:
                        penalidade += config.PESO_MESMO_DIA
                    elif distancia == 1:
                        penalidade += config.PESO_DIAS_CONSECUTIVOS
        return penalidade

    def _avaliar_sc_infraestrutura(self, genes: List) -> int:
        penalidade = 0
        for gene in genes:
            if gene.sala.id == "EXTERNA": continue

            excedente = gene.disciplina.numero_alunos - gene.sala.capacidade_maxima
            if excedente > 0:
                penalidade += (excedente ** 2) * config.PESO_ALUNO_EXCEDENTE

            vazios = gene.sala.capacidade_maxima - gene.disciplina.numero_alunos
            if vazios > 20:
                penalidade += (vazios - 20) * config.PESO_CADEIRA_VAZIA

            if gene.disciplina.prefere_sala_grande and gene.sala.capacidade_maxima < 60:
                penalidade += config.PESO_SALA_PEQUENA
        return penalidade

    def _avaliar_sc_pedagogia(self, genes: List) -> int:
        penalidade = 0
        for gene in genes:
            if gene.disciplina.turno_curso == "INTEGRAL" and gene.disciplina.periodo >= 5 and gene.horario not in config.TURNOS_MANHA:
                penalidade += config.PESO_TURNO_INCORRETO
        return penalidade

    def _avaliar_sc_jornada_docente(self, alocacoes_por_docente_dia: dict) -> int:
        penalidade = 0
        for (id_prof, dia), genes_no_dia in alocacoes_por_docente_dia.items():
            qtd_aulas = len(genes_no_dia)
            if id_prof != "EXT" and qtd_aulas > 2:
                excesso = qtd_aulas - 2
                penalidade += (excesso ** 2) * config.PESO_FADIGA_DOCENTE
        return penalidade

    def _avaliar_sc_jornada_aluno(self, alocacoes_por_periodo_dia: dict) -> int:
        penalidade = 0
        for (periodo, dia), genes_no_dia in alocacoes_por_periodo_dia.items():
            qtd_aulas = len(genes_no_dia)
            if qtd_aulas > 3:
                excesso = qtd_aulas - 3
                penalidade += (excesso ** 2) * config.PESO_SOBRECARGA_ALUNO

            if qtd_aulas >= 2:
                penalidade += (qtd_aulas - 1) * config.PESO_JANELA_OCIOSA
        return penalidade

    def _avaliar_sc_equidade(self, genes: List) -> int:
        penalidade = 0
        horarios_ruins_por_prof = defaultdict(int)
        for gene in genes:
            if gene.disciplina.id_professor != "EXT" and gene.horario in config.HORARIOS_RUINS:
                horarios_ruins_por_prof[gene.disciplina.id_professor] += 1

        for id_prof, contagem in horarios_ruins_por_prof.items():
            if contagem > 1:
                penalidade += config.PESO_HORARIO_RUIM
        return penalidade