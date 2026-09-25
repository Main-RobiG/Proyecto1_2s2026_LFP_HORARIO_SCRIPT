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
        
    # ---------------------------------------------------------------
    # Nucleo del AFD
    # ---------------------------------------------------------------

    def siguiente_token(self):

        while True:
            c = self._actual()

            if c is None:
                return None  # EOF

            if _es_espacio(c) or c == "\n":
                self._avanzar()
                continue

            if c == "#":
                # Puede ser inicio de comentario "##" o un '#' suelto (error).
                token_comentario = self._leer_comentario_o_error()
                if token_comentario is not None:
                    return token_comentario
                # Si _leer_comentario_o_error devolvio None fue un error de
                # caracter suelto ya registrado; seguimos buscando el
                # siguiente token real.
                continue

            break  # c es el inicio de un token "de verdad"

        linea_inicio = self.linea
        columna_inicio = self.columna
        c = self._actual()

        if c == '"':
            return self._leer_cadena(linea_inicio, columna_inicio)

        if _es_letra(c):
            return self._leer_identificador(linea_inicio, columna_inicio)

        if _es_digito(c):
            return self._leer_numero_u_hora(linea_inicio, columna_inicio)

        if c in SIMBOLOS:
            self._avanzar()
            return self._crear_token(c, "SIMBOLO", linea_inicio, columna_inicio)

        # Cualquier otro caracter no encaja en ningun patron valido.
        self._avanzar()
        self._registrar_error(c, CARACTER_NO_RECONOCIDO, linea_inicio, columna_inicio)
        return self.siguiente_token()  # sigue buscando el proximo token valido
    
    # ---------------------------------------------------------------
    # Sub-automatas por tipo de token
    # ---------------------------------------------------------------

    def _leer_comentario_o_error(self):

        linea_inicio = self.linea
        columna_inicio = self.columna
        self._avanzar()  # consume el primer '#'

        if self._actual() != "#":
            # '#' suelto: no es un comentario valido.
            self._registrar_error("#", CARACTER_NO_RECONOCIDO, linea_inicio, columna_inicio)
            return None

        self._avanzar()  # consume el segundo '#'
        lexema = "##"
        while self._actual() is not None and self._actual() != "\n":
            lexema += self._actual()
            self._avanzar()
        # No consumimos el '\n' aqui; el bucle principal lo hara.
        return self._crear_token(lexema, "COMENTARIO_LINEA", linea_inicio, columna_inicio)

    def _leer_cadena(self, linea_inicio, columna_inicio):
        """Estado q_cadena. Por decision B: todo lo que va entre comillas es CADENA."""
        self._avanzar()  # consume la comilla de apertura
        lexema = ""
        while True:
            c = self._actual()
            if c is None or c == "\n":
                self._registrar_error(lexema, CADENA_SIN_CERRAR, linea_inicio, columna_inicio)
                return self.siguiente_token()
            if c == '"':
                self._avanzar()  # consume la comilla de cierre
                return self._crear_token(lexema, "CADENA", linea_inicio, columna_inicio)
            lexema += c
            self._avanzar()


    # ---------------------------------------------------------------
    # Reconocimiento de identificadores, palabras reservadas y codigos
    # (decisiones A y C del manual tecnico)
    # ---------------------------------------------------------------

    def _leer_identificador(self, linea_inicio, columna_inicio):
      
        lexema = self._actual()
        self._avanzar()

        # Primero consumimos letras/digitos "normales" (parte alfanumerica).
        while _es_letra(self._actual()) or _es_digito(self._actual()):
            lexema += self._actual()
            self._avanzar()

        if self._actual() == "-":
            # q_ident_dash: posible CODIGO tipo letras(+digitos)-digitos
            return self._leer_codigo_con_guion(lexema, linea_inicio, columna_inicio)

        # No hay guion: clasificar contra palabras reservadas / enums.
        return self._clasificar_identificador_simple(lexema, linea_inicio, columna_inicio)

    def _leer_codigo_con_guion(self, prefijo, linea_inicio, columna_inicio):
        """Decision C: patron flexible letras(+digitos)-digitos, sin comillas."""
        lexema = prefijo + "-"
        self._avanzar()  # consume el '-'

        digitos = ""
        while _es_digito(self._actual()):
            digitos += self._actual()
            lexema += self._actual()
            self._avanzar()

        # Si tras los digitos viene otro guion o una letra pegada, el
        # patron letras(-digitos) se rompe: seguimos consumiendo hasta el
        # delimitador para reportar el lexema completo, pero es error.
        malformado = len(digitos) == 0
        while _es_letra(self._actual()) or self._actual() == "-":
            malformado = True
            lexema += self._actual()
            self._avanzar()
            while _es_digito(self._actual()):
                lexema += self._actual()
                self._avanzar()

        if malformado:
            self._registrar_error(lexema, CODIGO_MAL_FORMADO, linea_inicio, columna_inicio)
            return self.siguiente_token()

        return self._crear_token(lexema, "CODIGO", linea_inicio, columna_inicio)

    def _clasificar_identificador_simple(self, lexema, linea_inicio, columna_inicio):

        if lexema in PR_BLOQUE:
            tipo = "PR_BLOQUE"
        elif lexema in PR_ELEMENTO:
            tipo = "PR_ELEMENTO"
        elif lexema in PR_RELACION:
            tipo = "PR_RELACION"
        elif lexema in PR_ATRIBUTO:
            tipo = "PR_ATRIBUTO"
        elif lexema in DIA_VALIDOS:
            tipo = "DIA"
        elif lexema in CATEGORIA_VALIDOS:
            tipo = "CATEGORIA"
        else:
            # No es ninguna palabra reservada ni enum conocido.
            if self.ultimo_atributo == "dia":
                self._registrar_error(lexema, DIA_NO_RECONOCIDO, linea_inicio, columna_inicio)
            else:
                self._registrar_error(lexema, CODIGO_MAL_FORMADO, linea_inicio, columna_inicio)
            return self.siguiente_token()

        tok = self._crear_token(lexema, tipo, linea_inicio, columna_inicio)

        # Actualizamos la "memoria" de contexto solo con PR_ATRIBUTO.
        if tipo == "PR_ATRIBUTO":
            self.ultimo_atributo = lexema
        else:
            # Cualquier otro token "cierra" el contexto del atributo previo,
            # salvo ':' que es el separador natural entre atributo y valor.
            if not (tipo == "SIMBOLO" and lexema == ":"):
                self.ultimo_atributo = None

        return tok
    