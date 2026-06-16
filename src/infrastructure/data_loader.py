import csv
from pathlib import Path
from domain.professor import Professor
from domain.sala import Sala
from domain.disciplina import Disciplina


class DataLoader:
    def __init__(self, data_folder_name: str = 'data'):
        self.data_folder = Path(__file__).parent.parent.parent / data_folder_name

    def carregar_professores(self) -> dict:
        caminho_arquivo = self.data_folder / 'professores.csv'
        professores = {}

        with open(caminho_arquivo, mode='r', encoding='utf-8') as file:
            leitor_csv = csv.DictReader(file)
            for linha in leitor_csv:
                indisponibilidades = linha['horarios_indisponiveis'].split(';') if linha[
                    'horarios_indisponiveis'] else []

                prof = Professor(
                    id=linha['id'],
                    nome=linha['nome'],
                    horarios_indisponiveis=indisponibilidades
                )
                professores[prof.id] = prof

        return professores

    def carregar_salas(self) -> list:
        caminho_arquivo = self.data_folder / 'salas.csv'
        salas = []

        with open(caminho_arquivo, mode='r', encoding='utf-8') as file:
            leitor_csv = csv.DictReader(file)
            for linha in leitor_csv:
                sala = Sala(
                    id=linha['id'],
                    capacidade_maxima=int(linha['capacidade_maxima']),
                    is_lab=linha['is_lab'].strip().lower() == 'true'
                )
                salas.append(sala)

        return salas

    def carregar_disciplinas(self) -> list:
        caminho_arquivo = self.data_folder / 'disciplinas.csv'
        disciplinas = []

        with open(caminho_arquivo, mode='r', encoding='utf-8') as file:
            leitor_csv = csv.DictReader(file)
            for linha in leitor_csv:
                periodo_raw = linha.get('periodo', '').strip()
                periodo_val = int(periodo_raw) if periodo_raw else None

                curso_raw = linha.get('curso', '').strip()
                curso_val = curso_raw if curso_raw else None

                disciplina = Disciplina(
                    id=linha['id'].strip(),
                    nome=linha['nome'].strip(),
                    turma=linha['turma'].strip(),
                    vaga=int(linha['vaga']),
                    turno=linha['turno'].strip().upper(),
                    aulas_semanais=int(linha['aulas_semanais']),
                    curso=curso_val,
                    periodo=periodo_val,
                    lab=linha['lab'].strip().lower() == 'true',
                    id_professor=linha['id_professor'].strip()
                )

                disciplinas.append(disciplina)

        return disciplinas