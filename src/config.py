HORARIOS_DISPONIVEIS = [
    "Segunda_07h", "Segunda_09h", "Segunda_11h", "Segunda_14h", "Segunda_16h", "Segunda_18h", "Segunda_20h",
    "Terca_07h", "Terca_09h", "Terca_11h", "Terca_14h", "Terca_16h", "Terca_18h", "Terca_20h",
    "Quarta_07h", "Quarta_09h", "Quarta_11h", "Quarta_14h", "Quarta_16h", "Quarta_18h", "Quarta_20h",
    "Quinta_07h", "Quinta_09h", "Quinta_11h", "Quinta_14h", "Quinta_16h", "Quinta_18h", "Quinta_20h",
    "Sexta_07h", "Sexta_09h", "Sexta_11h", "Sexta_14h", "Sexta_16h", "Sexta_18h", "Sexta_20h",
]

TURNOS_MANHA = [h for h in HORARIOS_DISPONIVEIS if "07h" in h or "09h" in h or "11h" in h]

TURNOS_NOITE = [h for h in HORARIOS_DISPONIVEIS if "18h" in h or "20h" in h]

HORARIOS_PROIBIDOS = ["Quarta_16h"]

HORARIOS_RUINS = ["Segunda_07h", "Sexta_18h", "Sexta_20h"]

PESO_HARD = 1000

DIAS_DA_SEMANA = {
    "Segunda": 1,
    "Terca": 2,
    "Quarta": 3,
    "Quinta": 4,
    "Sexta": 5
}