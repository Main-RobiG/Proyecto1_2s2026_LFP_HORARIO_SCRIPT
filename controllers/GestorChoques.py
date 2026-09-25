SIMBOLOS_ESTRUCTURALES = {"{", "}", ";"}


class GestorChoques:

    def __init__(self, tokens):
        # Los comentarios no aportan estructura, se filtran.
        self._tokens = [t for t in tokens if t.tipo != "COMENTARIO_LINEA"]
        self._pos = 0
        self._n = len(self._tokens)

        self.cursos = []
        self.catedraticos = []
        self.aulas = []
        self.clases = []
        self.choques = []

    # ---------------------------------------------------------------
    # Utilidades de recorrido sobre la lista de tokens
    # ---------------------------------------------------------------

    def _actual(self):
        return self._tokens[self._pos] if self._pos < self._n else None

    def _avanzar(self):
        self._pos += 1

    def _es(self, tipo, lexema=None):
        t = self._actual()
        if t is None or t.tipo != tipo:
            return False
        if lexema is not None and t.lexema != lexema:
            return False
        return True

    # ---------------------------------------------------------------
    # Construccion del modelo (CURSOS / CATEDRATICOS / AULAS / CLASES)
    # ---------------------------------------------------------------

    def analizar(self):
        """Recorre los tokens, arma el modelo y detecta choques."""
        seccion_actual = None

        while self._actual() is not None:
            t = self._actual()

            if t.tipo == "PR_BLOQUE":
                seccion_actual = t.lexema
                self._avanzar()
                continue

            if t.tipo == "PR_ELEMENTO":
                elemento = self._parsear_elemento(t.lexema)
                if t.lexema == "curso":
                    self.cursos.append(elemento)
                elif t.lexema == "catedratico":
                    self.catedraticos.append(elemento)
                elif t.lexema == "aula":
                    self.aulas.append(elemento)
                elif t.lexema == "clase":
                    self.clases.append(elemento)
                continue

            if t.tipo == "SIMBOLO" and t.lexema in SIMBOLOS_ESTRUCTURALES:
                self._avanzar()
                continue

            # Cualquier otro token suelto a este nivel se ignora
            # (ya fue reportado como error por AnalizadorLexico si aplicaba).
            self._avanzar()

        self.choques = self._detectar_choques(self.clases)
        return {
            "cursos": self.cursos,
            "catedraticos": self.catedraticos,
            "aulas": self.aulas,
            "clases": self.clases,
            "choques": self.choques,
        }

    def _parsear_atributos(self):
        """Parsea '[ atributo: valor, atributo: valor, ... ]' -> dict."""
        atributos = {}
        if not self._es("SIMBOLO", "["):
            return atributos
        self._avanzar()  # consume '['

        while self._actual() is not None and not self._es("SIMBOLO", "]"):
            if self._es("PR_ATRIBUTO"):
                nombre_attr = self._actual().lexema
                self._avanzar()
                if self._es("SIMBOLO", ":"):
                    self._avanzar()
                valor = self._actual()
                atributos[nombre_attr] = valor.lexema if valor is not None else None
                self._avanzar()
            if self._es("SIMBOLO", ","):
                self._avanzar()

        if self._es("SIMBOLO", "]"):
            self._avanzar()  # consume ']'

        return atributos

    def _parsear_elemento(self, tipo_elemento):
        """Parsea un elemento curso/catedratico/aula/clase completo."""
        self._avanzar()  # consume la palabra reservada de elemento

        if self._es("SIMBOLO", ":"):
            self._avanzar()

        if tipo_elemento == "clase":
            curso_ref = self._leer_valor_referencia()
            if self._es("PR_RELACION", "con"):
                self._avanzar()
            catedratico_ref = self._leer_valor_referencia()
            if self._es("PR_RELACION", "en"):
                self._avanzar()
            aula_ref = self._leer_valor_referencia()

            atributos = self._parsear_atributos()
            if self._es("SIMBOLO", ","):
                self._avanzar()

            return {
                "curso_ref": curso_ref,
                "catedratico_ref": catedratico_ref,
                "aula_ref": aula_ref,
                "dia": atributos.get("dia"),
                "inicio": atributos.get("inicio"),
                "fin": atributos.get("fin"),
                "seccion": atributos.get("seccion"),
            }
        else:
            nombre = self._leer_valor_referencia()
            atributos = self._parsear_atributos()
            if self._es("SIMBOLO", ","):
                self._avanzar()

            return {"nombre": nombre, "atributos": atributos}

    def _leer_valor_referencia(self):
        """Lee un valor tipo CADENA o CODIGO (nombre/identificador) y avanza."""
        t = self._actual()
        if t is None or t.tipo not in ("CADENA", "CODIGO"):
            return None
        self._avanzar()
        return t.lexema

    # ---------------------------------------------------------------
    # Deteccion de choques (criterio 2.5)
    # ---------------------------------------------------------------

    @staticmethod
    def _hora_a_minutos(hora_str):
        """'07:00' -> 420. Slicing simple, no es tokenizacion."""
        if hora_str is None or len(hora_str) != 5:
            return None
        try:
            horas = int(hora_str[0:2])
            minutos = int(hora_str[3:5])
        except ValueError:
            return None
        return horas * 60 + minutos

    def _hay_traslape(self, clase_a, clase_b):
        ini_a = self._hora_a_minutos(clase_a["inicio"])
        fin_a = self._hora_a_minutos(clase_a["fin"])
        ini_b = self._hora_a_minutos(clase_b["inicio"])
        fin_b = self._hora_a_minutos(clase_b["fin"])
        if None in (ini_a, fin_a, ini_b, fin_b):
            return False
        return ini_a < fin_b and ini_b < fin_a

    def _detectar_choques(self, clases):
        """
        Compara cada par de clases: mismo dia + (mismo catedratico o
        misma aula) + bloque horario traslapado -> choque.
        """
        choques = []
        for i in range(len(clases)):
            for j in range(i + 1, len(clases)):
                a, b = clases[i], clases[j]

                if a["dia"] is None or a["dia"] != b["dia"]:
                    continue

                mismo_catedratico = (
                    a["catedratico_ref"] is not None
                    and a["catedratico_ref"] == b["catedratico_ref"]
                )
                misma_aula = (
                    a["aula_ref"] is not None and a["aula_ref"] == b["aula_ref"]
                )

                if not (mismo_catedratico or misma_aula):
                    continue

                if not self._hay_traslape(a, b):
                    continue

                if mismo_catedratico:
                    motivo = f"Mismo catedratico ({a['catedratico_ref']})"
                else:
                    motivo = f"Misma aula ({a['aula_ref']})"

                choques.append({
                    "clase_a": a,
                    "clase_b": b,
                    "dia": a["dia"],
                    "motivo": motivo,
                })
        return choques