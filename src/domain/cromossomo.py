from dataclasses import dataclass
from typing import List
from domain.gene import Gene

@dataclass
class Cromossomo:
    genes: List[Gene]
    fitness: int = 0