import os
import tkinter as tk
import webbrowser
from controllers.GestorChoques import GestorChoques
from controllers.GeneradorReportes import GeneradorReportes
from tkinter import filedialog, messagebox, ttk

from controllers.AnalizadorLexico import AnalizadorLexico


class Interfaz:

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("HorarioScript - Analizador Lexico")
        self.ventana.geometry("1050x650")

        self.ruta_archivo = None
        self.tokens = []
        self.errores = []

        self._construir_barra_superior()
        self._construir_tablas()

    # ---------------------------------------------------------------
    # Construccion de widgets
    # ---------------------------------------------------------------
    def _construir_barra_superior(self):
        
        barra = tk.Frame(self.ventana)
        barra.pack(fill="x", padx=10, pady=10)

        self.boton_cargar = tk.Button(barra, text="Cargar archivo .hor", command=self._cargar_archivo)
        self.boton_cargar.pack(side="left")

        self.etiqueta_archivo = tk.Label(barra, text="Ningun archivo cargado", fg="gray")
        self.etiqueta_archivo.pack(side="left", padx=10)

        self.boton_analizar = tk.Button(
            barra, text="Ejecutar analisis", command=self._ejecutar_analisis, state="disabled"
        )
        self.boton_analizar.pack(side="left", padx=10)

        self.boton_reportes = tk.Button(
            barra, text="Generar reportes HTML", command=self._generar_reportes, state="disabled"
        )
        self.boton_reportes.pack(side="left", padx=10)

        self.etiqueta_resumen = tk.Label(barra, text="", fg="blue")
        self.etiqueta_resumen.pack(side="left", padx=10)
    def _construir_tablas(self):
        paneles = tk.Frame(self.ventana)
        paneles.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- Panel izquierdo: tabla de tokens (criterio 2.3) ---
        panel_tokens = tk.LabelFrame(paneles, text="Tabla de Tokens")
        panel_tokens.pack(side="left", fill="both", expand=True, padx=(0, 5))

        columnas_tokens = ("numero", "lexema", "tipo", "linea", "columna")
        self.tabla_tokens = ttk.Treeview(panel_tokens, columns=columnas_tokens, show="headings")
        for col, texto, ancho in [
            ("numero", "#", 40),
            ("lexema", "Lexema", 160),
            ("tipo", "Tipo", 130),
            ("linea", "Linea", 50),
            ("columna", "Columna", 60),
        ]:
            self.tabla_tokens.heading(col, text=texto)
            self.tabla_tokens.column(col, width=ancho, anchor="w")
        self.tabla_tokens.pack(fill="both", expand=True, side="left")

        scroll_tokens = ttk.Scrollbar(panel_tokens, orient="vertical", command=self.tabla_tokens.yview)
        self.tabla_tokens.configure(yscrollcommand=scroll_tokens.set)
        scroll_tokens.pack(side="right", fill="y")

        # --- Panel derecho: tabla de errores (criterio 2.4) ---
        panel_errores = tk.LabelFrame(paneles, text="Tabla de Errores Lexicos")
        panel_errores.pack(side="left", fill="both", expand=True, padx=(5, 0))

        columnas_errores = ("numero", "lexema", "tipo", "descripcion", "linea", "columna")
        self.tabla_errores = ttk.Treeview(panel_errores, columns=columnas_errores, show="headings")
        for col, texto, ancho in [
            ("numero", "#", 40),
            ("lexema", "Lexema", 100),
            ("tipo", "Tipo de Error", 150),
            ("descripcion", "Descripcion", 220),
            ("linea", "Linea", 50),
            ("columna", "Columna", 60),
        ]:
            self.tabla_errores.heading(col, text=texto)
            self.tabla_errores.column(col, width=ancho, anchor="w")
        self.tabla_errores.pack(fill="both", expand=True, side="left")

        scroll_errores = ttk.Scrollbar(panel_errores, orient="vertical", command=self.tabla_errores.yview)
        self.tabla_errores.configure(yscrollcommand=scroll_errores.set)
        scroll_errores.pack(side="right", fill="y")

    # ---------------------------------------------------------------
    # Acciones (comandos de los botones)
    # ---------------------------------------------------------------

    def _cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona un archivo HorarioScript",
            filetypes=[("Archivos HorarioScript", "*.hor"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        self.ruta_archivo = ruta
        self.etiqueta_archivo.config(text=os.path.basename(ruta), fg="black")
        self.boton_analizar.config(state="normal")
        self.etiqueta_resumen.config(text="")

    def _ejecutar_analisis(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Sin archivo", "Primero carga un archivo .hor")
            return

        try:
            analizador = AnalizadorLexico(self.ruta_archivo)
        except OSError as e:
            messagebox.showerror("Error al abrir archivo", str(e))
            return

        self.tokens = []
        while True:
            tok = analizador.siguiente_token()
            if tok is None:
                break
            self.tokens.append(tok)

        self.errores = analizador.gestor_errores.obtener_errores()

        self.etiqueta_resumen.config(
            text=f"Tokens: {len(self.tokens)}   Errores: {len(self.errores)}"
        )
        self._llenar_tablas()
        self.boton_reportes.config(state="normal")

    def _llenar_tablas(self):
        self.tabla_tokens.delete(*self.tabla_tokens.get_children())
        for tok in self.tokens:
            self.tabla_tokens.insert("", "end", values=(tok.numero, tok.lexema, tok.tipo, tok.linea, tok.columna))

        self.tabla_errores.delete(*self.tabla_errores.get_children())
        for err in self.errores:
            self.tabla_errores.insert(
                "", "end",
                values=(err.numero, err.lexema, err.tipo, err.descripcion, err.linea, err.columna),
            )
            
    def _generar_reportes(self):
        gestor = GestorChoques(self.tokens)
        modelo = gestor.analizar()

        generador = GeneradorReportes(carpeta_salida="reportes")
        rutas = generador.generar_todos(modelo, self.errores)

        mensaje = f"Reportes generados en la carpeta 'reportes/':\n" + "\n".join(rutas.values())
        if modelo["choques"]:
            mensaje += f"\n\n¡Atencion! Se detectaron {len(modelo['choques'])} choque(s) de horario."
        messagebox.showinfo("Reportes generados", mensaje)

        webbrowser.open(f"file://{os.path.abspath(rutas['horario'])}")