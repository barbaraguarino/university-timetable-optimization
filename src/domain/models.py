from dataclasses import dataclass, field
from typing import List

@dataclass
class Professor:
    id: str
    nome: str
    horarios_indisponiveis: List[str] = field(default_factory=list)

    def is_disponivel(self, horario: str) -> bool:
        return horario not in self.horarios_indisponiveis

@dataclass
class Sala:
    id: str
    capacidade_maxima: int

@dataclass
class Disciplina:
    id: str
    nome: str
    id_professor: str
    numero_alunos: int
    periodo: int
    is_alta_demanda: bool
    is_preferencia: bool

@dataclass
class Gene:
    disciplina: Disciplina
    sala: Sala
    horario: str

@dataclass
class Cromossomo:
    genes: List[Gene]
    fitness: int = 0