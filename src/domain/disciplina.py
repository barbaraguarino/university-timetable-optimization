from dataclasses import dataclass
from typing import Optional

@dataclass
class Disciplina:
    id: str
    nome: str
    turma: str
    vaga: int
    turno:str
    aulas_semanais: int
    curso: Optional[str]
    periodo: Optional[int]
    lab: bool
    id_professor: str