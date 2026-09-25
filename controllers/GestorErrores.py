from models.ErrorLexico import ErrorLexico

CARACTER_NO_RECONOCIDO = "CARACTER_NO_RECONOCIDO"
CADENA_SIN_CERRAR = "CADENA_SIN_CERRAR"
DIA_NO_RECONOCIDO = "DIA_NO_RECONOCIDO"
CODIGO_MAL_FORMADO = "CODIGO_MAL_FORMADO"
HORA_FUERA_DE_RANGO = "HORA_FUERA_DE_RANGO"


class GestorErrores:
   
    def __init__(self):
        self._errores = []
        self._contador = 0

    def registrar(self, lexema, tipo, linea, columna, mensaje=None):
        """
        Registra un nuevo error. Si no se da 'mensaje', se genera uno
        por defecto siguiendo el formato EXACTO de la tabla 4.8.
        """
        self._contador += 1
        descripcion = mensaje or self._mensaje_por_defecto(tipo, lexema, linea, columna)
        error = ErrorLexico(self._contador, lexema, tipo, descripcion, linea, columna)
        self._errores.append(error)
        return error

    def _mensaje_por_defecto(self, tipo, lexema, linea, columna):
        
        if tipo == CARACTER_NO_RECONOCIDO:
            return f"Caracter no reconocido: '{lexema}' en linea {linea}, columna {columna}."
        elif tipo == CADENA_SIN_CERRAR:
            return f"Cadena sin cerrar iniciada en linea {linea}, columna {columna}."
        elif tipo == DIA_NO_RECONOCIDO:
            return f"Dia no reconocido: '{lexema}' en linea {linea}, columna {columna}."
        elif tipo == CODIGO_MAL_FORMADO:
            return f"Codigo mal formado: '{lexema}' en linea {linea}, columna {columna}."
        elif tipo == HORA_FUERA_DE_RANGO:
            return f"Hora fuera de rango (06:00-21:00): '{lexema}' en linea {linea}, columna {columna}."
        else:
            return f"Error lexico: '{lexema}' en linea {linea}, columna {columna}."

    def hay_errores(self):
        return len(self._errores) > 0

    def total_errores(self):
        return len(self._errores)

    def obtener_errores(self):
        """Devuelve la lista completa de ErrorLexico, en orden de aparicion."""
        return list(self._errores)

    def reiniciar(self):
        """Limpia el gestor para analizar un nuevo archivo .hor."""
        self._errores = []
        self._contador = 0