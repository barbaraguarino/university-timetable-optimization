import random
from typing import List, Dict
from domain.models import Disciplina, Sala, Professor, Gene, Cromossomo
import config


class Grasp:

    def __init__(self, professores: Dict[str, Professor], salas: List[Sala], disciplinas: List[Disciplina]):
        self.professores = professores
        self.salas = salas
        self.disciplinas = disciplinas

    def gerar_cromossoma(self) -> Cromossomo:
        genes = []
        salas_ocupadas = {h: set() for h in config.HORARIOS_DISPONIVEIS}
        professores_ocupados = {h: set() for h in config.HORARIOS_DISPONIVEIS}
        periodos_ocupados = {h: set() for h in config.HORARIOS_DISPONIVEIS}

        disciplinas_aleatorias = list(self.disciplinas)
        random.shuffle(disciplinas_aleatorias)

        for disciplina in disciplinas_aleatorias:
            for _ in range(disciplina.aulas_semanais):
                candidatos_validos = []

                for horario in config.HORARIOS_DISPONIVEIS:
                    if horario in config.HORARIOS_PROIBIDOS: continue
                    if horario in config.HORARIOS_PROIBIDOS: continue

                    prof = self.professores.get(disciplina.id_professor)
                    if prof and not prof.is_disponivel(horario): continue

                    if disciplina.instituto != "IC":
                        sala_escolhida = next(s for s in self.salas if s.id == "EXTERNA")
                        candidatos_validos.append((horario, sala_escolhida))
                        continue
                    if disciplina.id_professor in professores_ocupados[horario]: continue
                    if disciplina.periodo in periodos_ocupados[horario]: continue
                    if disciplina.turno_curso == "NOITE" and horario not in config.TURNOS_NOITE:
                        continue

                    for sala in self.salas:
                        if sala.id not in salas_ocupadas[horario]:
                            if disciplina.needs_lab == sala.is_lab:
                                candidatos_validos.append((horario, sala))

                if candidatos_validos:
                    horario_escolhido, sala_escolhida = random.choice(candidatos_validos)
                else:
                    horario_escolhido = random.choice(config.HORARIOS_DISPONIVEIS)
                    sala_escolhida = random.choice(self.salas)

                gene = Gene(disciplina=disciplina, sala=sala_escolhida, horario=horario_escolhido)
                genes.append(gene)

                salas_ocupadas[horario_escolhido].add(sala_escolhida.id)
                professores_ocupados[horario_escolhido].add(disciplina.id_professor)
                periodos_ocupados[horario_escolhido].add(disciplina.periodo)

        return Cromossomo(genes=genes)

    def gerar_populacao_inicial(self, tamanho_populacao: int) -> List[Cromossomo]:
        return [self.gerar_cromossoma() for _ in range(tamanho_populacao)]