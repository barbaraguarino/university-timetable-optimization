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

DIAS_DA_SEMANA = {
    "Segunda": 1, "Terca": 2, "Quarta": 3, "Quinta": 4, "Sexta": 5
}

### PESOS DAS PENALIDADES (FITNESS) ###

# Regras Rígidas
PESO_HARD = 1000

# Regras Flexíveis
PESO_ALUNO_EXCEDENTE = 5       # Multiplicador exponencial por aluno sem lugar
PESO_CADEIRA_VAZIA = 2         # Multiplicador linear por cadeira ociosa além do limite
PESO_SALA_PEQUENA = 50         # Penalidade por ignorar preferência de sala grande
PESO_TURNO_INCORRETO = 40      # Penalidade por ignorar preferência de turno
PESO_FADIGA_DOCENTE = 300      # Multiplicador exponencial para excesso de aulas do professor
PESO_SOBRECARGA_ALUNO = 50     # Multiplicador exponencial para excesso de aulas do período
PESO_JANELA_OCIOSA = 15        # Penalidade base por buracos na grelha
PESO_HORARIO_RUIM = 500        # Punição por desequilíbrio na distribuição de horários ingratos
PESO_DIAS_CONSECUTIVOS = 150   # Punição por aulas da mesma disciplina em dias colados
PESO_MESMO_DIA = 400           # Punição severa por 4h seguidas da mesma disciplina