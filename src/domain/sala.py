from dataclasses import dataclass

@dataclass
class Sala:
    id: str
    capacidade_maxima: int
    is_lab: bool