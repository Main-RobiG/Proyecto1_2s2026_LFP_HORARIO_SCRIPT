from models.Token import Token
from controllers.GestorErrores import (
    GestorErrores,
    CARACTER_NO_RECONOCIDO,
    CADENA_SIN_CERRAR,
    DIA_NO_RECONOCIDO,
    CODIGO_MAL_FORMADO,
    HORA_FUERA_DE_RANGO,
)

# --- Palabras reservadas del lenguaje (secciones 4.5 - 4.7 del enunciado) ---

PR_BLOQUE = {"HORARIO", "CURSOS", "CATEDRATICOS", "AULAS", "CLASES"}
PR_ELEMENTO = {"curso", "catedratico", "aula", "clase"}
PR_RELACION = {"con", "en"}
PR_ATRIBUTO = {
    "codigo", "creditos", "categoria", "capacidad",
    "edificio", "dia", "inicio", "fin", "seccion",
}
DIA_VALIDOS = {"LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"}
CATEGORIA_VALIDOS = {"TITULAR", "INTERINO", "AUXILIAR"}

# Simbolos de un solo caracter con significado sintactico propio.
SIMBOLOS = {"{", "}", "[", "]", ":", ",", ";"}

HORA_MIN = (6, 0)    # 06:00
HORA_MAX = (21, 0)   # 21:00


