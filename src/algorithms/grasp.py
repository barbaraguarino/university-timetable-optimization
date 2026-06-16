import random
from typing import List, Dict, Tuple
from domain.disciplina import Disciplina
from domain.sala import Sala
from domain.professor import Professor
from domain.gene import Gene
from domain.cromossomo import Cromossomo
import config

def _obter_horarios_permitidos(disciplina: Disciplina) -> List[str]:
    if disciplina.turno == "MATUTINO":
        return config.TURNO_MATUTINO
    elif disciplina.turno == "VESPERTINO":
        return config.TURNO_VESPERTINO
    elif disciplina.turno == "NOTURNO":
        return config.TURNO_NOTURNO
    return config.HORARIOS_DISPONIVEIS

def _calcular_custo_insercao(disciplina: Disciplina, horario: str, sala: Sala,
                             dias_alocados: set, prof_aulas_dia: int) -> int:
    custo = 0

    excedente = disciplina.vaga - sala.capacidade_maxima

    if excedente > 0:
        custo += (excedente ** 2) * config.PESO_ALUNO_EXCEDENTE

    vazios = sala.capacidade_maxima - disciplina.vaga
    if vazios > 20:
        custo += (vazios - 20) * config.PESO_CADEIRA_VAZIA

    dia_semana = horario.split("_")[0]
    if dia_semana in dias_alocados:
        custo += config.PESO_MESMO_DIA

    if prof_aulas_dia >= 2:
        custo += config.PESO_FADIGA_DOCENTE

    if horario in config.HORARIOS_RUINS:
        custo += config.PESO_HORARIO_RUIM

    return custo

def _atualizar_estado_ocupacao(estado: dict, gene: Gene, dias_alocados: set) -> None:
    h = gene.horario
    disc = gene.disciplina

    estado["salas_ocupadas"][h].add(gene.sala.id)
    estado["professores_ocupados"][h].add(disc.id_professor)

    if disc.periodo is not None and disc.curso is not None:
        estado["periodos_ocupados"][h].add((disc.periodo, disc.curso, disc.turma))

    dia_escolhido = h.split("_")[0]
    dias_alocados.add(dia_escolhido)

    if disc.id_professor in estado["prof_aulas_dia"]:
        estado["prof_aulas_dia"][disc.id_professor][dia_escolhido] += 1

class Grasp:

    def __init__(self, professores: Dict[str, Professor], salas: List[Sala], disciplinas: List[Disciplina]):
        self.professores = professores
        self.salas = salas
        self.disciplinas = disciplinas
        self.tamanho_rcl = 3

    def gerar_populacao_inicial(self, tamanho_populacao: int) -> List[Cromossomo]:
        return [self.gerar_cromossoma() for _ in range(tamanho_populacao)]

    def gerar_cromossoma(self) -> Cromossomo:
        genes = []

        estado = {
            "salas_ocupadas": {h: set() for h in config.HORARIOS_DISPONIVEIS},
            "professores_ocupados": {h: set() for h in config.HORARIOS_DISPONIVEIS},
            "periodos_ocupados": {h: set() for h in config.HORARIOS_DISPONIVEIS},
            "prof_aulas_dia": {prof.id: {dia: 0 for dia in config.DIAS_DA_SEMANA.keys()} for prof in
                               self.professores.values()}
        }

        disciplinas_aleatorias = list(self.disciplinas)
        random.shuffle(disciplinas_aleatorias)

        for disciplina in disciplinas_aleatorias:
            dias_alocados = set()

            for _ in range(disciplina.aulas_semanais):
                horarios_permitidos = _obter_horarios_permitidos(disciplina)

                candidatos = self._buscar_candidatos_validos(disciplina, horarios_permitidos, estado, dias_alocados)

                if candidatos:
                    horario_escolhido, sala_escolhida = self._escolher_via_rcl(candidatos)
                else:
                    horario_escolhido, sala_escolhida = self._aplicar_fallback(disciplina, horarios_permitidos, estado)

                gene = Gene(disciplina=disciplina, sala=sala_escolhida, horario=horario_escolhido)
                genes.append(gene)

                _atualizar_estado_ocupacao(estado, gene, dias_alocados)

        cromossomo = Cromossomo(genes=genes)
        cromossomo.genes.sort(key=lambda g: f"{g.disciplina.id}_{g.disciplina.turma}")
        return cromossomo

    def _buscar_candidatos_validos(self, disciplina: Disciplina, horarios_permitidos: List[str],
                                   estado: dict, dias_alocados: set) -> List[Tuple[int, str, Sala]]:
        candidatos = []
        prof = self.professores.get(disciplina.id_professor)

        for horario in horarios_permitidos:
            if horario in config.HORARIOS_PROIBIDOS:
                continue

            if prof and not prof.is_disponivel(horario):
                continue
            if disciplina.id_professor in estado["professores_ocupados"][horario]:
                continue

            if disciplina.periodo is not None and disciplina.curso is not None:
                chave_periodo = (disciplina.periodo, disciplina.curso, disciplina.turma)
                if chave_periodo in estado["periodos_ocupados"][horario]:
                    continue

            dia_semana = horario.split("_")[0]
            aulas_prof_neste_dia = estado["prof_aulas_dia"].get(disciplina.id_professor, {}).get(dia_semana, 0)

            for sala in self.salas:
                if sala.id not in estado["salas_ocupadas"][horario] and disciplina.lab == sala.is_lab:
                    custo = _calcular_custo_insercao(disciplina, horario, sala, dias_alocados,
                                                          aulas_prof_neste_dia)
                    candidatos.append((custo, horario, sala))

        return candidatos

    def _escolher_via_rcl(self, candidatos: List[Tuple[int, str, Sala]]) -> Tuple[str, Sala]:
        candidatos.sort(key=lambda x: x[0])
        tamanho_rcl_real = min(self.tamanho_rcl, len(candidatos))
        rcl = candidatos[:tamanho_rcl_real]
        _, horario_escolhido, sala_escolhida = random.choice(rcl)
        return horario_escolhido, sala_escolhida

    def _aplicar_fallback(self, disciplina: Disciplina, horarios_permitidos: List[str], estado: dict) -> Tuple[str, Sala]:
        horarios_seguros = []
        for h in horarios_permitidos:
            prof_livre = disciplina.id_professor not in estado["professores_ocupados"][h]
            turma_livre = True

            if disciplina.periodo is not None and disciplina.curso is not None:
                if (disciplina.periodo, disciplina.curso, disciplina.turma) in estado["periodos_ocupados"][h]:
                    turma_livre = False

            if prof_livre and turma_livre:
                horarios_seguros.append(h)
        if horarios_seguros:
            horario_escolhido = random.choice(horarios_seguros)
        else:
            horarios_prof_livre = [h for h in horarios_permitidos if
                                   disciplina.id_professor not in estado["professores_ocupados"][h]]
            horario_escolhido = random.choice(horarios_prof_livre) if horarios_prof_livre else random.choice(
                horarios_permitidos)
        salas_compativeis = [s for s in self.salas if s.is_lab == disciplina.lab]
        sala_escolhida = random.choice(salas_compativeis) if salas_compativeis else random.choice(self.salas)
        return horario_escolhido, sala_escolhida