import random
from typing import List, Dict
from domain.disciplina import Disciplina
from domain.sala import Sala
from domain.professor import Professor
from domain.gene import Gene
from domain.cromossomo import Cromossomo
import config


class Grasp:

    def __init__(self, professores: Dict[str, Professor], salas: List[Sala], disciplinas: List[Disciplina]):
        self.professores = professores
        self.salas = salas
        self.disciplinas = disciplinas
        self.tamanho_rcl = 3

    def _calcular_custo_insercao(self, disciplina: Disciplina, horario: str, sala: Sala,
                                 dias_alocados: set, prof_aulas_dia: int) -> int:
        custo = 0

        excedente = disciplina.numero_alunos - sala.capacidade_maxima
        if excedente > 0:
            custo += (excedente ** 2) * config.PESO_ALUNO_EXCEDENTE

        vazios = sala.capacidade_maxima - disciplina.numero_alunos
        if vazios > 20:
            custo += (vazios - 20) * config.PESO_CADEIRA_VAZIA

        if disciplina.prefere_sala_grande and sala.capacidade_maxima < 60:
            custo += config.PESO_SALA_PEQUENA

        dia_semana = horario.split("_")[0]
        if dia_semana in dias_alocados:
            custo += config.PESO_MESMO_DIA

        if prof_aulas_dia >= 2:
            custo += config.PESO_FADIGA_DOCENTE

        if horario in config.HORARIOS_RUINS:
            custo += config.PESO_HORARIO_RUIM

        if disciplina.turno_curso == "INTEGRAL" and disciplina.periodo >= 5 and horario not in config.TURNOS_MANHA:
            custo += config.PESO_TURNO_INCORRETO

        return custo

    def gerar_cromossoma(self) -> Cromossomo:
        genes = []
        salas_ocupadas = {h: set() for h in config.HORARIOS_DISPONIVEIS}
        professores_ocupados = {h: set() for h in config.HORARIOS_DISPONIVEIS}
        periodos_ocupados = {h: set() for h in config.HORARIOS_DISPONIVEIS}

        prof_aulas_dia = {prof.id: {dia: 0 for dia in config.DIAS_DA_SEMANA.keys()} for prof in
                          self.professores.values()}

        disciplinas_aleatorias = list(self.disciplinas)
        random.shuffle(disciplinas_aleatorias)

        for disciplina in disciplinas_aleatorias:
            dias_alocados = set()

            for _ in range(disciplina.aulas_semanais):
                candidatos = []

                horarios_permitidos = config.TURNOS_NOITE if disciplina.turno_curso == "NOITE" else config.HORARIOS_DISPONIVEIS

                for horario in horarios_permitidos:
                    if horario in config.HORARIOS_PROIBIDOS: continue

                    prof = self.professores.get(disciplina.id_professor)
                    if prof and not prof.is_disponivel(horario): continue
                    if disciplina.id_professor in professores_ocupados[horario]: continue

                    chave_periodo = (disciplina.periodo, disciplina.turno_curso)
                    if chave_periodo in periodos_ocupados[horario]: continue

                    dia_semana = horario.split("_")[0]
                    aulas_prof_neste_dia = prof_aulas_dia.get(disciplina.id_professor, {}).get(dia_semana, 0)

                    for sala in self.salas:
                        if sala.id not in salas_ocupadas[horario]:
                            if disciplina.needs_lab == sala.is_lab:
                                custo = self._calcular_custo_insercao(
                                    disciplina, horario, sala, dias_alocados, aulas_prof_neste_dia
                                )
                                candidatos.append((custo, horario, sala))

                if candidatos:
                    candidatos.sort(key=lambda x: x[0])

                    tamanho_rcl_real = min(self.tamanho_rcl, len(candidatos))
                    rcl = candidatos[:tamanho_rcl_real]

                    _, horario_escolhido, sala_escolhida = random.choice(rcl)
                else:
                    horario_escolhido = random.choice(horarios_permitidos)
                    salas_compativeis = [s for s in self.salas if s.is_lab == disciplina.needs_lab]
                    sala_escolhida = random.choice(salas_compativeis) if salas_compativeis else random.choice(
                        self.salas)

                gene = Gene(disciplina=disciplina, sala=sala_escolhida, horario=horario_escolhido)
                genes.append(gene)

                salas_ocupadas[horario_escolhido].add(sala_escolhida.id)
                professores_ocupados[horario_escolhido].add(disciplina.id_professor)
                periodos_ocupados[horario_escolhido].add((disciplina.periodo, disciplina.turno_curso))

                dia_escolhido = horario_escolhido.split("_")[0]
                dias_alocados.add(dia_escolhido)
                if disciplina.id_professor in prof_aulas_dia:
                    prof_aulas_dia[disciplina.id_professor][dia_escolhido] += 1

        cromossomo = Cromossomo(genes=genes)
        cromossomo.genes.sort(key=lambda g: g.disciplina.id)

        return cromossomo

    def gerar_populacao_inicial(self, tamanho_populacao: int) -> List[Cromossomo]:
        return [self.gerar_cromossoma() for _ in range(tamanho_populacao)]