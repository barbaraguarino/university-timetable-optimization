from dataclasses import dataclass

@dataclass
class Disciplina:
    id: str
    nome: str
    id_professor: str
    numero_alunos: int
    periodo: int
    is_alta_demanda: bool
    prefere_sala_grande: bool
    aulas_semanais: int
    needs_lab: bool
    turno_curso: str