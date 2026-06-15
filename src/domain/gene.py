from dataclasses import dataclass
from domain.disciplina import Disciplina
from domain.sala import Sala

@dataclass
class Gene:
    disciplina: Disciplina
    sala: Sala
    horario: str