from dataclasses import dataclass, field
from typing import List

@dataclass
class Professor:
    id: str
    nome: str
    horarios_indisponiveis: List[str] = field(default_factory=list)

    def is_disponivel(self, horario: str) -> bool:
        return horario not in self.horarios_indisponiveis