class Token:

    def __init__(self, numero, lexema, tipo, linea, columna):
        self.numero = numero
        self.lexema = lexema
        self.tipo = tipo
        self.linea = linea
        self.columna = columna

    def __str__(self):
        return f"Token({self.numero}, {self.lexema!r}, {self.tipo}, linea={self.linea}, columna={self.columna})"

    def to_dict(self):
        """Facilita exportar el token a la tabla de la GUI o a un reporte HTML."""
        return {
            "numero": self.numero,
            "lexema": self.lexema,
            "tipo": self.tipo,
            "linea": self.linea,
            "columna": self.columna,
        }