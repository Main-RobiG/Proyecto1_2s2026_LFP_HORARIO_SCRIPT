class ErrorLexico:
   
    def __init__(self, numero, lexema, tipo, descripcion, linea, columna):
        self.numero = numero
        self.lexema = lexema
        self.tipo = tipo
        self.descripcion = descripcion
        self.linea = linea
        self.columna = columna

    def __str__(self):
        return f"ErrorLexico({self.numero}, {self.tipo}, {self.lexema!r}, linea={self.linea}, columna={self.columna})"

    def to_dict(self):
        """Facilita exportar el error a la tabla de la GUI o a un reporte HTML."""
        return {
            "numero": self.numero,
            "lexema": self.lexema,
            "tipo": self.tipo,
            "descripcion": self.descripcion,
            "linea": self.linea,
            "columna": self.columna,
        }