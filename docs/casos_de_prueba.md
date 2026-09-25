# Casos de Prueba — HorarioScript

Cada caso se ejecutó cargando el archivo `.hor` correspondiente desde
la interfaz gráfica y presionando "Ejecutar análisis". Los resultados
fueron verificados manualmente contra lo esperado.

| # | Caso | Archivo | Qué prueba | Resultado esperado | Resultado obtenido |
|---|------|---------|------------|---------------------|---------------------|
| 1 | Horario válido completo | `examples/horario_valido.hor` | AFD reconoce correctamente los 12 tipos de token en un archivo bien formado | 149 tokens, 0 errores | ✅ 149 tokens, 0 errores |
| 2 | Carácter no reconocido | `examples/horario_con_errores.hor` | Detecta un símbolo `@` fuera de una cadena | 1 error `CARACTER_NO_RECONOCIDO` | ✅ Detectado en línea 3 |
| 3 | Cadena sin cerrar | `examples/horario_con_errores.hor` | Detecta una comilla de apertura sin su cierre antes de fin de línea | 1 error `CADENA_SIN_CERRAR` | ✅ Detectado en línea 6 |
| 4 | Día no reconocido | `examples/horario_con_errores.hor` | Detecta `DOMINGO` como valor de atributo `dia` (no está entre los 6 días válidos) | 1 error `DIA_NO_RECONOCIDO` | ✅ Detectado en línea 12 |
| 5 | Hora fuera de rango | `examples/horario_con_errores.hor` | Detecta `25:00` como hora inválida (fuera de 06:00-21:00) | 1 error `HORA_FUERA_DE_RANGO` | ✅ Detectado en línea 13 |
| 6 | Código mal formado | `examples/horario_con_errores.hor` | Detecta `DOC-9-9` (doble guión) como código con formato inválido | 1 error `CODIGO_MAL_FORMADO` | ✅ Detectado en línea 14 |
| 7 | Recuperación de errores (modo pánico) | `examples/horario_con_errores.hor` | El análisis continúa después de cada error, sin detenerse | Los 5 errores anteriores se reportan juntos en un solo análisis, más los tokens válidos del resto del archivo | ✅ 5 errores detectados, 122 tokens |
| 8 | Choque de horario por catedrático | `examples/horario_con_choque.hor` | Dos clases del mismo catedrático (`DOC-001`), mismo día, con bloques horarios traslapados | 1 choque detectado, motivo "Mismo catedratico" | ✅ 1 choque, `LUNES`, `DOC-001` |
| 9 | Choque de horario por aula | `examples/horario_choque_por_aula.hor` | Dos clases distintas en la misma aula (`AUL-101`), mismo día, horarios traslapados | 1 choque detectado, motivo "Misma aula" | ✅ 1 choque, `MARTES`, `AUL-101` |
| 10 | Bloques vacíos (caso borde) | `examples/horario_vacio.hor` | El AFD y el parser de choques no truenan cuando `CURSOS`, `CATEDRATICOS`, `AULAS` y `CLASES` no tienen elementos | 0 clases, 0 choques, 0 errores, sin excepciones | ✅ Ejecuta sin errores |
| 11 | Generación de reportes HTML | `examples/horario_con_choque.hor` | Los 3 reportes obligatorios + el de errores se generan correctamente en `reportes/` | 4 archivos `.html` generados, el choque resaltado en rojo en el Reporte 1 | ✅ 4 archivos generados |

## Cómo reproducir cualquier caso

1. Ejecutar `python main.py`.
2. Clic en "Cargar archivo .hor" y seleccionar el archivo de la columna "Archivo".
3. Clic en "Ejecutar análisis".
4. Comparar el resumen de tokens/errores mostrado contra la columna "Resultado esperado".
5. (Opcional) Clic en "Generar reportes HTML" para el caso 11.