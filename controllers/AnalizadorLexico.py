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


def _es_letra(c):
    """True si c es una letra. Usa isalpha(), permitido: no tokeniza."""
    return c is not None and c.isalpha()


def _es_digito(c):
    """True si c es un digito. Usa isdigit(), permitido: no tokeniza."""
    return c is not None and c.isdigit()

def _es_espacio(c):
    """Espacio, tab o retorno de carro (el salto de linea se maneja aparte)."""
    return c in (" ", "\t", "\r")

class AnalizadorLexico:
   
    def __init__(self, ruta_archivo):
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            self.texto = f.read()

        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.longitud = len(self.texto)

        self.gestor_errores = GestorErrores()
        self._contador_tokens = 0

        self.ultimo_atributo = None

    # ---------------------------------------------------------------
    # Utilidades de bajo nivel (unica forma permitida de "mirar" el texto)
    # ---------------------------------------------------------------

    def _actual(self):
        """Caracter en la posicion actual, o None si llegamos a EOF."""
        if self.pos >= self.longitud:
            return None
        return self.texto[self.pos]

    def _avanzar(self):
        """Consume el caracter actual y actualiza linea/columna."""
        c = self._actual()
        if c is None:
            return
        self.pos += 1
        if c == "\n":
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1

    def _crear_token(self, lexema, tipo, linea_inicio, columna_inicio):
        self._contador_tokens += 1
        return Token(self._contador_tokens, lexema, tipo, linea_inicio, columna_inicio)

    def _registrar_error(self, lexema, tipo, linea_inicio, columna_inicio, mensaje=None):
        self.gestor_errores.registrar(lexema, tipo, linea_inicio, columna_inicio, mensaje)