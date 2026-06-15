import csv
from pathlib import Path
from domain.models import Professor, Sala, Disciplina


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
                    capacidade_maxima=int(linha['capacidade_maxima'])
                )
                salas.append(sala)

        return salas

    def carregar_disciplinas(self) -> list:
        caminho_arquivo = self.data_folder / 'disciplinas.csv'
        disciplinas = []

        with open(caminho_arquivo, mode='r', encoding='utf-8') as file:
            leitor_csv = csv.DictReader(file)
            for linha in leitor_csv:
                disciplina = Disciplina(
                    id=linha['id'],
                    nome=linha['nome'],
                    id_professor=linha['id_professor'],
                    numero_alunos=int(linha['numero_alunos']),
                    periodo=int(linha['periodo']),
                    is_alta_demanda=linha['is_alta_demanda'].strip().lower() == 'true',
                    is_preferencia=linha['is_preferencia'].strip().lower() == 'true',
                    aulas_semanais=int(linha['aulas_semanais'])
                )
                disciplinas.append(disciplina)

        return disciplinas