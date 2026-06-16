from collections import defaultdict
from typing import Dict, Tuple, List
from domain.cromossomo import Cromossomo
from domain.professor import Professor
from domain.gene import Gene
import config


class FitnessEvaluator:

    def __init__(self, professores: Dict[str, Professor]):
        self.professores = professores

    def calcular_fitness(self, cromossomo: Cromossomo) -> int:
        penalidade_total = 0
        penalidades_disc = defaultdict(int)

        (
            alocacoes_por_horario,
            alocacoes_por_docente_dia,
            alocacoes_por_periodo_dia,
            alocacoes_por_disciplina,
            horarios_ruins_por_prof
        ) = self._indexar_cromossomo(cromossomo)

        for gene in cromossomo.genes:
            disc_key = f"{gene.disciplina.id}_{gene.disciplina.turma}"
            penalidade_gene = self._avaliar_regras_locais(gene)

            penalidades_disc[disc_key] += penalidade_gene
            penalidade_total += penalidade_gene

        penalidade_total += self._avaliar_hc_por_horario(alocacoes_por_horario)
        penalidade_total += self._avaliar_sc_distribuicao_semanal(alocacoes_por_disciplina)
        penalidade_total += self._avaliar_sc_jornada_docente(alocacoes_por_docente_dia)
        penalidade_total += self._avaliar_sc_jornada_aluno(alocacoes_por_periodo_dia)
        penalidade_total += self._avaliar_sc_equidade(horarios_ruins_por_prof)

        cromossomo.fitness = penalidade_total
        cromossomo.disciplinas_problematicas = [
            d_key for d_key, mult in sorted(penalidades_disc.items(), key=lambda item: item[1], reverse=True)
            if mult > 0
        ]

        return penalidade_total

    def _avaliar_regras_locais(self, gene: Gene) -> int:
        penalidade = 0
        disc = gene.disciplina
        sala = gene.sala
        horario = gene.horario

        prof = self.professores.get(disc.id_professor)
        if prof and not prof.is_disponivel(horario):
            penalidade += config.PESO_HARD

        if disc.lab != sala.is_lab:
            penalidade += config.PESO_HARD

        if disc.turno == "MATUTINO" and horario not in config.TURNO_MATUTINO:
            penalidade += config.PESO_HARD
        elif disc.turno == "VESPERTINO" and horario not in config.TURNO_VESPERTINO:
            penalidade += config.PESO_HARD
        elif disc.turno == "NOTURNO" and horario not in config.TURNO_NOTURNO:
            penalidade += config.PESO_HARD

        excedente = disc.vaga - sala.capacidade_maxima
        if excedente > 0:
            penalidade += (excedente ** 2) * config.PESO_ALUNO_EXCEDENTE

        vazios = sala.capacidade_maxima - disc.vaga
        if vazios > 20:
            penalidade += (vazios - 20) * config.PESO_CADEIRA_VAZIA

        return penalidade

    @staticmethod
    def _indexar_cromossomo(cromossomo: Cromossomo) -> Tuple:
        alocacoes_por_horario = defaultdict(list)
        alocacoes_por_docente_dia = defaultdict(list)
        alocacoes_por_periodo_dia = defaultdict(list)
        alocacoes_por_disciplina = defaultdict(list)
        horarios_ruins_por_prof = defaultdict(int)

        for gene in cromossomo.genes:
            horario = gene.horario
            dia = horario.split("_")[0]
            disc = gene.disciplina
            disc_key = f"{disc.id}_{disc.turma}"

            alocacoes_por_horario[horario].append(gene)
            alocacoes_por_docente_dia[(disc.id_professor, dia)].append(gene)
            alocacoes_por_disciplina[disc_key].append(gene)

            if disc.periodo is not None and disc.curso is not None:
                alocacoes_por_periodo_dia[(disc.periodo, disc.curso, disc.turma, dia)].append(gene)

            if horario in config.HORARIOS_RUINS:
                horarios_ruins_por_prof[disc.id_professor] += 1

        return (alocacoes_por_horario, alocacoes_por_docente_dia, alocacoes_por_periodo_dia,
                alocacoes_por_disciplina, horarios_ruins_por_prof)

    @staticmethod
    def _avaliar_hc_por_horario(alocacoes_por_horario: dict) -> int:
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

                if gene.disciplina.periodo is not None and gene.disciplina.curso is not None:
                    chave_periodo = (gene.disciplina.periodo, gene.disciplina.curso, gene.disciplina.turma)
                    if chave_periodo in periodos_vistos:
                        penalidade += config.PESO_HARD
                    periodos_vistos.add(chave_periodo)
        return penalidade

    @staticmethod
    def _avaliar_sc_distribuicao_semanal(alocacoes_por_disciplina: dict) -> int:
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

    @staticmethod
    def _avaliar_sc_jornada_docente(alocacoes_por_docente_dia: dict) -> int:
        penalidade = 0
        for genes_no_dia in alocacoes_por_docente_dia.values():
            qtd_aulas = len(genes_no_dia)
            if qtd_aulas > 2:
                penalidade += ((qtd_aulas - 2) ** 2) * config.PESO_FADIGA_DOCENTE
        return penalidade

    @staticmethod
    def _avaliar_sc_jornada_aluno(alocacoes_por_periodo_dia: dict) -> int:
        penalidade = 0
        for genes_no_dia in alocacoes_por_periodo_dia.values():
            qtd_aulas = len(genes_no_dia)
            if qtd_aulas > 3:
                penalidade += ((qtd_aulas - 3) ** 2) * config.PESO_SOBRECARGA_ALUNO
            if qtd_aulas >= 2:
                penalidade += (qtd_aulas - 1) * config.PESO_JANELA_OCIOSA
        return penalidade

    @staticmethod
    def _avaliar_sc_equidade(horarios_ruins_por_prof: dict) -> int:
        penalidade = 0
        for contagem in horarios_ruins_por_prof.values():
            if contagem > 1:
                penalidade += config.PESO_HORARIO_RUIM
        return penalidade

    def auditar_solucao(self, cromossomo: Cromossomo) -> List[dict]:
        relatorio = []
        (alocacoes_por_horario, alocacoes_por_docente_dia, alocacoes_por_periodo_dia,
         alocacoes_por_disciplina, horarios_ruins_por_prof) = self._indexar_cromossomo(cromossomo)

        for gene in cromossomo.genes:
            disc = gene.disciplina
            sala = gene.sala
            horario = gene.horario
            prof = self.professores.get(disc.id_professor)

            if prof and not prof.is_disponivel(horario):
                relatorio.append({"Tipo": "HARD", "Regra": "Prof. Indisponível", "Disciplina": disc.nome,
                                  "Detalhe": f"Prof: {prof.nome} em {horario}", "Pontos": config.PESO_HARD})
            if disc.lab != sala.is_lab:
                relatorio.append({"Tipo": "HARD", "Regra": "Incompatibilidade Lab", "Disciplina": disc.nome,
                                  "Detalhe": f"Requisita Lab: {disc.lab} | Sala: {sala.is_lab}",
                                  "Pontos": config.PESO_HARD})

            if disc.turno == "MATUTINO" and horario not in config.TURNO_MATUTINO:
                relatorio.append({"Tipo": "HARD", "Regra": "Turno Incorreto", "Disciplina": disc.nome,
                                  "Detalhe": f"Alocada {horario}", "Pontos": config.PESO_HARD})
            elif disc.turno == "VESPERTINO" and horario not in config.TURNO_VESPERTINO:
                relatorio.append({"Tipo": "HARD", "Regra": "Turno Incorreto", "Disciplina": disc.nome,
                                  "Detalhe": f"Alocada {horario}", "Pontos": config.PESO_HARD})
            elif disc.turno == "NOTURNO" and horario not in config.TURNO_NOTURNO:
                relatorio.append({"Tipo": "HARD", "Regra": "Turno Incorreto", "Disciplina": disc.nome,
                                  "Detalhe": f"Alocada {horario}", "Pontos": config.PESO_HARD})

            excedente = disc.vaga - sala.capacidade_maxima
            if excedente > 0:
                relatorio.append({"Tipo": "SOFT", "Regra": "Superlotação", "Disciplina": disc.nome,
                                  "Detalhe": f"{excedente} alunos em pé na sala {sala.id}",
                                  "Pontos": (excedente ** 2) * config.PESO_ALUNO_EXCEDENTE})

            vazios = sala.capacidade_maxima - disc.vaga
            if vazios > 20:
                relatorio.append({"Tipo": "SOFT", "Regra": "Cadeiras Vazias", "Disciplina": disc.nome,
                                  "Detalhe": f"{vazios} lugares ociosos na {sala.id}",
                                  "Pontos": (vazios - 20) * config.PESO_CADEIRA_VAZIA})

        for horario, genes in alocacoes_por_horario.items():
            if horario in config.HORARIOS_PROIBIDOS:
                relatorio.append(
                    {"Tipo": "HARD", "Regra": "Horário Proibido", "Disciplina": "Várias", "Detalhe": horario,
                     "Pontos": config.PESO_HARD * len(genes)})

            professores_vistos = set()
            salas_vistas = set()
            periodos_vistos = set()

            for gene in genes:
                if gene.disciplina.id_professor in professores_vistos:
                    relatorio.append(
                        {"Tipo": "HARD", "Regra": "Choque de Professor", "Disciplina": gene.disciplina.nome,
                         "Detalhe": f"Prof: {gene.disciplina.id_professor} em {horario}", "Pontos": config.PESO_HARD})
                professores_vistos.add(gene.disciplina.id_professor)

                if gene.sala.id in salas_vistas:
                    relatorio.append({"Tipo": "HARD", "Regra": "Choque de Sala", "Disciplina": gene.disciplina.nome,
                                      "Detalhe": f"Sala: {gene.sala.id} em {horario}", "Pontos": config.PESO_HARD})
                salas_vistas.add(gene.sala.id)

                if gene.disciplina.periodo is not None and gene.disciplina.curso is not None:
                    chave_periodo = (gene.disciplina.periodo, gene.disciplina.curso, gene.disciplina.turma)
                    if chave_periodo in periodos_vistos:
                        relatorio.append(
                            {"Tipo": "HARD", "Regra": "Choque de Turma", "Disciplina": gene.disciplina.nome,
                             "Detalhe": f"Turma {chave_periodo} em {horario}", "Pontos": config.PESO_HARD})
                    periodos_vistos.add(chave_periodo)

        for genes_da_disc in alocacoes_por_disciplina.values():
            if len(genes_da_disc) > 1:
                dias = [config.DIAS_DA_SEMANA[g.horario.split("_")[0]] for g in genes_da_disc]
                dias.sort()
                for i in range(len(dias) - 1):
                    distancia = dias[i + 1] - dias[i]
                    if distancia == 0:
                        relatorio.append({"Tipo": "SOFT", "Regra": "Aulas no Mesmo Dia",
                                          "Disciplina": genes_da_disc[0].disciplina.nome, "Detalhe": "4 horas seguidas",
                                          "Pontos": config.PESO_MESMO_DIA})
                    elif distancia == 1:
                        relatorio.append({"Tipo": "SOFT", "Regra": "Dias Consecutivos",
                                          "Disciplina": genes_da_disc[0].disciplina.nome,
                                          "Detalhe": "Aulas sem intervalo", "Pontos": config.PESO_DIAS_CONSECUTIVOS})

        for (id_prof, dia), genes_no_dia in alocacoes_por_docente_dia.items():
            qtd_aulas = len(genes_no_dia)
            if qtd_aulas > 2:
                relatorio.append({"Tipo": "SOFT", "Regra": "Fadiga Docente", "Disciplina": "Várias",
                                  "Detalhe": f"Prof {id_prof} com {qtd_aulas} aulas na {dia}",
                                  "Pontos": ((qtd_aulas - 2) ** 2) * config.PESO_FADIGA_DOCENTE})

        for (periodo, curso, turma, dia), genes_no_dia in alocacoes_por_periodo_dia.items():
            qtd_aulas = len(genes_no_dia)
            if qtd_aulas > 3:
                relatorio.append({"Tipo": "SOFT", "Regra": "Sobrecarga Discente", "Disciplina": "Várias",
                                  "Detalhe": f"Turma {curso}-{periodo}-{turma} com {qtd_aulas} aulas na {dia}",
                                  "Pontos": ((qtd_aulas - 3) ** 2) * config.PESO_SOBRECARGA_ALUNO})
            if qtd_aulas >= 2:
                relatorio.append({"Tipo": "SOFT", "Regra": "Janela Ociosa", "Disciplina": "Várias",
                                  "Detalhe": f"Turma {curso}-{periodo}-{turma} teve janelas na {dia}",
                                  "Pontos": (qtd_aulas - 1) * config.PESO_JANELA_OCIOSA})

        return relatorio