HORARIOS_DISPONIVEIS = [
    "Segunda_07h", "Segunda_09h", "Segunda_11h", "Segunda_14h", "Segunda_16h", "Segunda_18h", "Segunda_20h",
    "Terca_07h", "Terca_09h", "Terca_11h", "Terca_14h", "Terca_16h", "Terca_18h", "Terca_20h",
    "Quarta_07h", "Quarta_09h", "Quarta_11h", "Quarta_14h", "Quarta_16h", "Quarta_18h", "Quarta_20h",
    "Quinta_07h", "Quinta_09h", "Quinta_11h", "Quinta_14h", "Quinta_16h", "Quinta_18h", "Quinta_20h",
    "Sexta_07h", "Sexta_09h", "Sexta_11h", "Sexta_14h", "Sexta_16h", "Sexta_18h", "Sexta_20h",
]

TURNO_MATUTINO = [h for h in HORARIOS_DISPONIVEIS if "07h" in h or "09h" in h or "11h" in h]
TURNO_VESPERTINO = [h for h in HORARIOS_DISPONIVEIS if "14h" in h or "16h" in h]
TURNO_NOTURNO = [h for h in HORARIOS_DISPONIVEIS if "18h" in h or "20h" in h]

HORARIOS_PROIBIDOS = ["Quarta_16h"]
HORARIOS_RUINS = ["Segunda_07h", "Sexta_18h", "Sexta_20h"]

DIAS_DA_SEMANA = {
    "Segunda": 1, "Terca": 2, "Quarta": 3, "Quinta": 4, "Sexta": 5
}

### PESOS DAS PENALIDADES (FITNESS) ###

PESO_HARD = 1000

PESO_ALUNO_EXCEDENTE = 5
PESO_CADEIRA_VAZIA = 2
PESO_SALA_PEQUENA = 50
PESO_TURNO_INCORRETO = 40
PESO_FADIGA_DOCENTE = 300
PESO_SOBRECARGA_ALUNO = 50
PESO_JANELA_OCIOSA = 15
PESO_HORARIO_RUIM = 500
PESO_DIAS_CONSECUTIVOS = 150
PESO_MESMO_DIA = 400