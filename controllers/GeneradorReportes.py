import os
class GeneradorReportes:
 
    UMBRALES_CARGA = [
        (0, 4, "BAJA", "#3498db"),
        (5, 10, "NORMAL", "#2ecc71"),
        (11, 15, "ALTA", "#e67e22"),
        (16, 9999, "SATURADA", "#e74c3c"),
    ]
    DIAS_ORDEN = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"]

    def __init__(self, carpeta_salida="reportes"):
        self.carpeta_salida = carpeta_salida
        os.makedirs(self.carpeta_salida, exist_ok=True)

    def _estilos(self):
        return """
        <style>
            body { font-family: Arial, Helvetica, sans-serif; margin: 24px; background: #f4f6f8; color: #222; }
            h1 { color: #1a2634; } h2 { color: #2c3e50; margin-top: 32px; }
            table { border-collapse: collapse; width: 100%; margin-top: 12px; background: white; }
            th, td { border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; font-size: 14px; }
            th { background: #1a2634; color: white; }
            tr:nth-child(even) { background: #f8f9fa; }
            .choque { background: #f8d7da !important; font-weight: bold; }
            .confirmado { background: #d4edda; }
            .badge { padding: 3px 8px; border-radius: 4px; color: white; font-size: 12px; }
            .kpis { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px; }
            .kpi { background: white; border: 1px solid #d0d7de; border-radius: 8px; padding: 16px 20px; min-width: 160px; }
            .kpi .valor { font-size: 28px; font-weight: bold; color: #1a2634; }
            .kpi .etiqueta { font-size: 13px; color: #667; }
            .barra-fondo { background: #e9ecef; border-radius: 4px; width: 100%; height: 14px; overflow: hidden; }
            .barra-relleno { background: #2ecc71; height: 100%; }
            .barra-relleno.alta { background: #e74c3c; }
        </style>
        """

    def _indexar(self, modelo):
        cursos_por_codigo = {c["atributos"].get("codigo"): c for c in modelo["cursos"]}
        catedraticos_por_codigo = {c["atributos"].get("codigo"): c for c in modelo["catedraticos"]}
        aulas_por_ref = {}
        for a in modelo["aulas"]:
            aulas_por_ref[a["nombre"]] = a
            if a["atributos"].get("codigo"):
                aulas_por_ref[a["atributos"]["codigo"]] = a
        return cursos_por_codigo, catedraticos_por_codigo, aulas_por_ref

    @staticmethod
    def _hora_a_minutos(hora_str):
        if hora_str is None or len(hora_str) != 5:
            return None
        try:
            return int(hora_str[0:2]) * 60 + int(hora_str[3:5])
        except ValueError:
            return None

    def _ids_en_choque(self, choques):
        ids = set()
        for ch in choques:
            ids.add(id(ch["clase_a"]))
            ids.add(id(ch["clase_b"]))
        return ids

    # --- Reporte 1: Horario semanal por seccion ---

    def generar_reporte_horario(self, modelo, nombre_archivo="reporte1_horario.html"):
        cursos_por_codigo, catedraticos_por_codigo, aulas_por_ref = self._indexar(modelo)
        ids_choque = self._ids_en_choque(modelo["choques"])
        clases_ordenadas = sorted(
            modelo["clases"],
            key=lambda c: (self.DIAS_ORDEN.index(c["dia"]) if c["dia"] in self.DIAS_ORDEN else 99, self._hora_a_minutos(c["inicio"]) or 0),
        )
        filas = ""
        for c in clases_ordenadas:
            curso = cursos_por_codigo.get(c["curso_ref"])
            catedratico = catedraticos_por_codigo.get(c["catedratico_ref"])
            en_choque = id(c) in ids_choque
            clase_css = "choque" if en_choque else "confirmado"
            estado = "CHOQUE DE HORARIO" if en_choque else "CONFIRMADO"
            filas += f"""<tr class="{clase_css}"><td>{c['dia'] or '-'}</td><td>{c['inicio'] or '-'} - {c['fin'] or '-'}</td><td>{curso['nombre'] if curso else c['curso_ref']}</td><td>{catedratico['nombre'] if catedratico else c['catedratico_ref']}</td><td>{c['aula_ref'] or '-'}</td><td>{c['seccion'] or '-'}</td><td>{estado}</td></tr>"""
        html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Reporte 1 - Horario Semanal</title>{self._estilos()}</head><body>
    <h1>Reporte 1 - Horario Semanal por Seccion</h1>
    <p>Total de clases: {len(modelo['clases'])} | Choques detectados: {len(modelo['choques'])}</p>
    <table><tr><th>Dia</th><th>Horario</th><th>Curso</th><th>Catedratico</th><th>Aula</th><th>Seccion</th><th>Estado</th></tr>
    {filas if filas else '<tr><td colspan="7">Sin clases registradas</td></tr>'}</table></body></html>"""
        return self._guardar(nombre_archivo, html)

    # --- Reporte 2: Carga de catedraticos ---

    def _nivel_de_carga(self, horas):
        for minimo, maximo, etiqueta, color in self.UMBRALES_CARGA:
            if minimo <= horas <= maximo:
                return etiqueta, color
        return "SATURADA", "#e74c3c"

    def generar_reporte_catedraticos(self, modelo, nombre_archivo="reporte2_catedraticos.html"):
        filas = ""
        for cat in modelo["catedraticos"]:
            codigo = cat["atributos"].get("codigo")
            categoria = cat["atributos"].get("categoria", "-")
            clases_de_cat = [c for c in modelo["clases"] if c["catedratico_ref"] == codigo]
            minutos_totales = 0
            for c in clases_de_cat:
                ini = self._hora_a_minutos(c["inicio"]); fin = self._hora_a_minutos(c["fin"])
                if ini is not None and fin is not None and fin > ini:
                    minutos_totales += fin - ini
            horas_totales = round(minutos_totales / 60, 1)
            cursos_distintos = len(set(c["curso_ref"] for c in clases_de_cat))
            secciones_distintas = len(set(c["seccion"] for c in clases_de_cat if c["seccion"]))
            nivel, color = self._nivel_de_carga(horas_totales)
            filas += f"""<tr><td>{cat['nombre']}</td><td>{codigo or '-'}</td><td>{categoria}</td><td>{horas_totales} hrs</td><td>{cursos_distintos}</td><td>{secciones_distintas}</td><td><span class="badge" style="background:{color}">{nivel}</span></td></tr>"""
        html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Reporte 2 - Carga de Catedraticos</title>{self._estilos()}</head><body>
    <h1>Reporte 2 - Carga de Catedraticos</h1>
    <p>Umbrales: BAJA 1-4h, NORMAL 5-10h, ALTA 11-15h, SATURADA 16h+ (definidos en el Manual Tecnico).</p>
    <table><tr><th>Nombre</th><th>Codigo</th><th>Categoria</th><th>Horas semanales</th><th>Cursos</th><th>Secciones</th><th>Nivel de carga</th></tr>
    {filas if filas else '<tr><td colspan="7">Sin catedraticos registrados</td></tr>'}</table></body></html>"""
        return self._guardar(nombre_archivo, html)

    # --- Reporte 3: Estadistico general del ciclo ---

    def generar_reporte_estadistico(self, modelo, nombre_archivo="reporte3_estadistico.html"):
        total_cursos = len(modelo["cursos"]); total_catedraticos = len(modelo["catedraticos"])
        total_aulas = len(modelo["aulas"]); total_clases = len(modelo["clases"]); total_choques = len(modelo["choques"])
        horas_por_cat = {}
        for c in modelo["clases"]:
            ini = self._hora_a_minutos(c["inicio"]); fin = self._hora_a_minutos(c["fin"])
            if ini is None or fin is None or fin <= ini:
                continue
            horas_por_cat[c["catedratico_ref"]] = horas_por_cat.get(c["catedratico_ref"], 0) + (fin - ini) / 60
        promedio_horas = round(sum(horas_por_cat.values()) / total_catedraticos, 1) if total_catedraticos else 0
        cat_mayor_carga = max(horas_por_cat, key=horas_por_cat.get) if horas_por_cat else None
        # Supuesto documentado en el Manual Tecnico: 6 dias x 15 horas institucionales (06:00-21:00).
        TOTAL_HORAS_DISPONIBLES = 6 * 15
        horas_por_aula = {}; clases_por_aula = {}
        for c in modelo["clases"]:
            ini = self._hora_a_minutos(c["inicio"]); fin = self._hora_a_minutos(c["fin"])
            if ini is None or fin is None or fin <= ini:
                continue
            horas_por_aula[c["aula_ref"]] = horas_por_aula.get(c["aula_ref"], 0) + (fin - ini) / 60
            clases_por_aula[c["aula_ref"]] = clases_por_aula.get(c["aula_ref"], 0) + 1
        aula_mayor_ocupacion = max(horas_por_aula, key=horas_por_aula.get) if horas_por_aula else None
        filas_aulas = ""
        for aula in modelo["aulas"]:
            ref = aula["nombre"]
            horas = round(horas_por_aula.get(ref, 0), 1)
            num_clases = clases_por_aula.get(ref, 0)
            porcentaje = round((horas / TOTAL_HORAS_DISPONIBLES) * 100, 1)
            clase_barra = "alta" if porcentaje > 80 else ""
            fila_css = "choque" if porcentaje > 80 else ""
            filas_aulas += f"""<tr class="{fila_css}"><td>{ref}</td><td>{num_clases}</td><td>{porcentaje}%<div class="barra-fondo"><div class="barra-relleno {clase_barra}" style="width:{min(porcentaje,100)}%"></div></div></td></tr>"""
        html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Reporte 3 - Estadistico General</title>{self._estilos()}</head><body>
    <h1>Reporte 3 - Estadistico General del Ciclo</h1>
    <div class="kpis">
        <div class="kpi"><div class="valor">{total_cursos}</div><div class="etiqueta">Cursos</div></div>
        <div class="kpi"><div class="valor">{total_catedraticos}</div><div class="etiqueta">Catedraticos</div></div>
        <div class="kpi"><div class="valor">{total_aulas}</div><div class="etiqueta">Aulas</div></div>
        <div class="kpi"><div class="valor">{total_clases}</div><div class="etiqueta">Clases programadas</div></div>
        <div class="kpi"><div class="valor">{total_choques}</div><div class="etiqueta">Choques detectados</div></div>
        <div class="kpi"><div class="valor">{promedio_horas}h</div><div class="etiqueta">Promedio horas/catedratico</div></div>
    </div>
    <p><strong>Catedratico con mayor carga:</strong> {cat_mayor_carga or '-'} ({round(horas_por_cat.get(cat_mayor_carga, 0), 1) if cat_mayor_carga else 0} hrs)</p>
    <p><strong>Aula con mayor ocupacion:</strong> {aula_mayor_ocupacion or '-'}</p>
    <h2>Ocupacion por aula</h2>
    <p style="font-size:13px;color:#667">Supuesto: {TOTAL_HORAS_DISPONIBLES} horas disponibles por semana (6 dias x 15 horas institucionales). Aulas con ocupacion mayor al 80% se resaltan en rojo.</p>
    <table><tr><th>Aula</th><th>Clases asignadas</th><th>% de ocupacion</th></tr>
    {filas_aulas if filas_aulas else '<tr><td colspan="3">Sin aulas registradas</td></tr>'}</table></body></html>"""
        return self._guardar(nombre_archivo, html)

    # --- Reporte adicional: errores lexicos (exigido en 4.8) ---

    def generar_reporte_errores(self, errores, nombre_archivo="reporte_errores.html"):
        filas = ""
        for e in errores:
            filas += f"""<tr><td>{e.numero}</td><td>{e.lexema}</td><td>{e.tipo}</td><td>{e.descripcion}</td><td>{e.linea}</td><td>{e.columna}</td></tr>"""
        html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Reporte de Errores Lexicos</title>{self._estilos()}</head><body>
    <h1>Reporte de Errores Lexicos</h1><p>Total de errores detectados: {len(errores)}</p>
    <table><tr><th>#</th><th>Lexema</th><th>Tipo de error</th><th>Descripcion</th><th>Linea</th><th>Columna</th></tr>
    {filas if filas else '<tr><td colspan="6">Sin errores detectados</td></tr>'}</table></body></html>"""
        return self._guardar(nombre_archivo, html)

    def _guardar(self, nombre_archivo, html):
        ruta = os.path.join(self.carpeta_salida, nombre_archivo)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(html)
        return ruta

    def generar_todos(self, modelo, errores):
        """Genera los 3 reportes obligatorios + el de errores. Devuelve las 4 rutas."""
        return {
            "horario": self.generar_reporte_horario(modelo),
            "catedraticos": self.generar_reporte_catedraticos(modelo),
            "estadistico": self.generar_reporte_estadistico(modelo),
            "errores": self.generar_reporte_errores(errores),
        }