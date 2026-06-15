from collections import defaultdict
from typing import Dict
from domain.cromossomo import Cromossomo
from domain.professor import Professor
import config


class FitnessEvaluator:

    def __init__(self, professores: Dict[str, Professor]):
        self.professores = professores

    def calcular_fitness(self, cromossomo: Cromossomo) -> int:
        penalidade = 0

        alocacoes_por_horario = defaultdict(list)
        alocacoes_por_docente_dia = defaultdict(list)
        alocacoes_por_periodo_dia = defaultdict(list)
        alocacoes_por_disciplina = defaultdict(list)
        horarios_ruins_por_prof = defaultdict(int)

        for gene in cromossomo.genes:
            horario = gene.horario
            dia = horario.split("_")[0]
            disc = gene.disciplina
            sala = gene.sala

            alocacoes_por_horario[horario].append(gene)
            alocacoes_por_docente_dia[(disc.id_professor, dia)].append(gene)
            alocacoes_por_periodo_dia[(disc.periodo, dia)].append(gene)
            alocacoes_por_disciplina[disc.id].append(gene)

            if horario in config.HORARIOS_RUINS:
                horarios_ruins_por_prof[disc.id_professor] += 1

            prof = self.professores.get(disc.id_professor)
            if prof and not prof.is_disponivel(horario):
                penalidade += config.PESO_HARD

            if disc.needs_lab != sala.is_lab:
                penalidade += config.PESO_HARD

            if disc.turno_curso == "NOITE" and horario not in config.TURNOS_NOITE:
                penalidade += config.PESO_HARD

            excedente = disc.numero_alunos - sala.capacidade_maxima
            if excedente > 0:
                penalidade += (excedente ** 2) * config.PESO_ALUNO_EXCEDENTE

            vazios = sala.capacidade_maxima - disc.numero_alunos
            if vazios > 20:
                penalidade += (vazios - 20) * config.PESO_CADEIRA_VAZIA

            if disc.prefere_sala_grande and sala.capacidade_maxima < 60:
                penalidade += config.PESO_SALA_PEQUENA

            if disc.turno_curso == "INTEGRAL" and disc.periodo >= 5 and horario not in config.TURNOS_MANHA:
                penalidade += config.PESO_TURNO_INCORRETO

        penalidade += self._avaliar_hc_por_horario(alocacoes_por_horario)
        penalidade += self._avaliar_sc_distribuicao_semanal(alocacoes_por_disciplina)
        penalidade += self._avaliar_sc_jornada_docente(alocacoes_por_docente_dia)
        penalidade += self._avaliar_sc_jornada_aluno(alocacoes_por_periodo_dia)
        penalidade += self._avaliar_sc_equidade(horarios_ruins_por_prof)

        cromossomo.fitness = penalidade
        return penalidade

    def _avaliar_hc_por_horario(self, alocacoes_por_horario: dict) -> int:
        penalidade = 0
        for horario, genes in alocacoes_por_horario.items():
            if horario in config.HORARIOS_PROIBIDOS:
                penalidade += config.PESO_HARD * len(genes)

            professores_vistos = set()
            salas_vistas = set()
            periodos_vistos = set()

            for gene in genes:
                if gene.disciplina.id_professor in professores_vistos:
                    penalidade += config.PESO_HARD
                professores_vistos.add(gene.disciplina.id_professor)

                if gene.sala.id in salas_vistas:
                    penalidade += config.PESO_HARD
                salas_vistas.add(gene.sala.id)

                chave_periodo = (gene.disciplina.periodo, gene.disciplina.turno_curso)
                if chave_periodo in periodos_vistos:
                    penalidade += config.PESO_HARD
                periodos_vistos.add(chave_periodo)
        return penalidade

    def _avaliar_sc_distribuicao_semanal(self, alocacoes_por_disciplina: dict) -> int:
        penalidade = 0
        for genes_da_disc in alocacoes_por_disciplina.values():
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

    def _avaliar_sc_jornada_docente(self, alocacoes_por_docente_dia: dict) -> int:
        penalidade = 0
        for genes_no_dia in alocacoes_por_docente_dia.values():
            qtd_aulas = len(genes_no_dia)
            if qtd_aulas > 2:
                penalidade += ((qtd_aulas - 2) ** 2) * config.PESO_FADIGA_DOCENTE
        return penalidade

    def _avaliar_sc_jornada_aluno(self, alocacoes_por_periodo_dia: dict) -> int:
        penalidade = 0
        for genes_no_dia in alocacoes_por_periodo_dia.values():
            qtd_aulas = len(genes_no_dia)
            if qtd_aulas > 3:
                penalidade += ((qtd_aulas - 3) ** 2) * config.PESO_SOBRECARGA_ALUNO
            if qtd_aulas >= 2:
                penalidade += (qtd_aulas - 1) * config.PESO_JANELA_OCIOSA
        return penalidade

    def _avaliar_sc_equidade(self, horarios_ruins_por_prof: dict) -> int:
        penalidade = 0
        for contagem in horarios_ruins_por_prof.values():
            if contagem > 1:
                penalidade += config.PESO_HORARIO_RUIM
        return penalidade