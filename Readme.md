# HorarioScript — Analizador Léxico

Proyecto 1 del curso de Lenguajes Formales y de Programación (2S-2026).
Analizador léxico para el lenguaje
**HorarioScript**, con interfaz gráfica en Tkinter, detección de
choques de horario y generación de reportes HTML.

**Autor(a):** Sergio Roberto Gudiel Sian
**Carné:** 201404365
**Curso / Sección:** Lenguajes Formales de Programación, Sección N

## Descripción del proyecto

HorarioScript es un mini-lenguaje declarativo para describir el
horario de un ciclo académico (cursos, catedráticos, aulas y clases).
Este proyecto implementa la **fase de análisis léxico**: un AFD manual
que reconoce 12 tipos de token, detecta y reporta errores léxicos sin
detener el análisis (modo pánico), y a partir de esos tokens reconstruye
el horario para detectar choques y generar reportes.

## Requisitos

- Python 3.10 o superior (no requiere librerías externas; Tkinter viene
  incluido con Python en Windows).

## Instalación y ejecución

```bash
git clone https://github.com/[tu-usuario]/[tu-repo].git
cd [tu-repo]
python main.py
```

Se abrirá la interfaz gráfica. Pasos dentro de la aplicación:

1. **Cargar archivo .hor** — selecciona un archivo HorarioScript (hay
   ejemplos listos en `examples/`).
2. **Ejecutar análisis** — corre el AFD y llena la tabla de tokens y
   la tabla de errores léxicos.
3. **Generar reportes HTML** — construye el modelo del horario, detecta
   choques, y genera 4 reportes HTML en la carpeta `reportes/` (se crea
   automáticamente), abriendo el primero en el navegador.

## Estructura del proyecto
```
├── main.py # Punto de entrada de la aplicacion
├── models/
│ ├── Token.py # Modelo de un token reconocido
│ └── ErrorLexico.py # Modelo de un error lexico
├── controllers/
│ ├── AnalizadorLexico.py # AFD manual (siguiente_token())
│ ├── GestorErrores.py # Acumula errores en modo panico
│ ├── GestorChoques.py # Reconstruye el horario y detecta choques
│ └── GeneradorReportes.py # Genera los reportes HTML
├── views/
│ └── Interfaz.py # GUI en Tkinter
├── examples/ # Archivos .hor de prueba
├── docs/ # Manual Tecnico y Manual de Usuario
└── reportes/ # Salida generada (ignorada por git)
```


## Tipos de token reconocidos

`PR_BLOQUE`, `PR_ELEMENTO`, `PR_RELACION`, `PR_ATRIBUTO`, `DIA`,
`CATEGORIA`, `CODIGO`, `CADENA`, `HORA`, `ENTERO`, `SIMBOLO`,
`COMENTARIO_LINEA`.

## Errores léxicos detectados

`CARACTER_NO_RECONOCIDO`, `CADENA_SIN_CERRAR`, `DIA_NO_RECONOCIDO`,
`CODIGO_MAL_FORMADO`, `HORA_FUERA_DE_RANGO`.

## Decisiones de diseño relevantes

Documentadas a detalle en `docs/manual_tecnico.md`. Resumen:

- **PR_ATRIBUTO** se creó como tipo de token reservado propio (no
  estaba explícito en el enunciado, pero el ejemplo de la sección 4.6
  lo exige).
- Todo lo que aparece entre comillas dobles es **CADENA**, sin
  excepción; **CODIGO** solo aplica a texto sin comillas.
- Se agregó el error **HORA_FUERA_DE_RANGO** (fuera de 06:00-21:00),
  no estaba en la tabla original de errores.

## Casos de prueba

Ver `docs/casos_de_prueba.md` para el detalle de cada caso y su
resultado esperado. Archivos de prueba en `examples/`.