MAPA_DIAS = {"Segunda": 0, "Terca": 1, "Quarta": 2, "Quinta": 3, "Sexta": 4}
MAPA_HORAS = {"07h": 0, "09h": 1, "11h": 2, "14h": 3, "16h": 4, "18h": 5, "20h": 6}
DIAS_NOME = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta"]
HORAS_NOME = ["07h", "09h", "11h", "14h", "16h", "18h", "20h"]

def str_to_id(horario_str: str) -> int:
    dia, hora = horario_str.split("_")
    return (MAPA_DIAS[dia] * 7) + MAPA_HORAS[hora]

def id_to_str(horario_id: int) -> str:
    return f"{DIAS_NOME[horario_id // 7]}_{HORAS_NOME[horario_id % 7]}"

HORARIOS_DISPONIVEIS = list(range(35))

TURNO_MATUTINO = [str_to_id(h) for h in ["Segunda_07h", "Segunda_09h", "Segunda_11h", "Terca_07h", "Terca_09h", "Terca_11h", "Quarta_07h", "Quarta_09h", "Quarta_11h", "Quinta_07h", "Quinta_09h", "Quinta_11h", "Sexta_07h", "Sexta_09h", "Sexta_11h"]]
TURNO_VESPERTINO = [str_to_id(h) for h in ["Segunda_14h", "Segunda_16h", "Terca_14h", "Terca_16h", "Quarta_14h", "Quarta_16h", "Quinta_14h", "Quinta_16h", "Sexta_14h", "Sexta_16h"]]
TURNO_NOTURNO = [str_to_id(h) for h in ["Segunda_18h", "Segunda_20h", "Terca_18h", "Terca_20h", "Quarta_18h", "Quarta_20h", "Quinta_18h", "Quinta_20h", "Sexta_18h", "Sexta_20h"]]

HORARIOS_PROIBIDOS = [str_to_id("Quarta_16h")]
HORARIOS_RUINS = [str_to_id(h) for h in ["Segunda_07h", "Sexta_18h", "Sexta_20h"]]


DIAS_DA_SEMANA = {"Segunda": 0, "Terca": 1, "Quarta": 2, "Quinta": 3, "Sexta": 4}

### PESOS DAS PENALIDADES (FITNESS) ###

PESO_HARD = 1000

PESO_ALUNO_EXCEDENTE = 5
PESO_CADEIRA_VAZIA = 2
PESO_SALA_PEQUENA = 50
PESO_FADIGA_DOCENTE = 300
PESO_SOBRECARGA_ALUNO = 50
PESO_JANELA_OCIOSA = 15
PESO_HORARIO_RUIM = 500
PESO_DIAS_CONSECUTIVOS = 150
PESO_MESMO_DIA = 400