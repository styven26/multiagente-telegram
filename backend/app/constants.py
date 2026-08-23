"""Constantes globales: temas del curso, textos y emojis del bot."""

# --- Grafo de conocimiento: Fundamentos de Programación ---
# El ID es la clave que se usará en la BD, en el contenido y en los datasets de ML.
# NO cambiar estos IDs una vez que existan datos.
TEMAS = {
    "T1_variables": {
        "nombre": "Variables y asignación",
        "orden": 1,
        "prerrequisitos": [],
        "emoji": "📦",
    },
    "T2_tipos_datos": {
        "nombre": "Tipos de datos",
        "orden": 2,
        "prerrequisitos": ["T1_variables"],
        "emoji": "🔢",
    },
    "T3_estructuras_control": {
        "nombre": "Estructuras de control",
        "orden": 3,
        "prerrequisitos": ["T2_tipos_datos"],
        "emoji": "🔀",
    },
    "T4_funciones": {
        "nombre": "Funciones",
        "orden": 4,
        "prerrequisitos": ["T3_estructuras_control"],
        "emoji": "⚙️",
    },
    "T5_estructuras_datos": {
        "nombre": "Estructuras de datos",
        "orden": 5,
        "prerrequisitos": ["T4_funciones"],
        "emoji": "📚",
    },
    "T6_archivos_excepciones": {
        "nombre": "Archivos y excepciones",
        "orden": 6,
        "prerrequisitos": ["T4_funciones"],
        "emoji": "📄",
    },
}

# --- Tipos de evento (materia prima de las métricas Lean y del SAKT) ---
class Evento:
    INICIO = "inicio"
    CONSENTIMIENTO = "consentimiento"
    CAPSULA_ENTREGADA = "capsula_entregada"
    CAPSULA_COMPLETADA = "capsula_completada"
    QUIZ_INICIADO = "quiz_iniciado"
    RESPUESTA = "respuesta"
    QUIZ_COMPLETADO = "quiz_completado"
    ABANDONO = "abandono"

# --- Estados de la respuesta ---
CORRECTA = "correcta"
INCORRECTA = "incorrecta"