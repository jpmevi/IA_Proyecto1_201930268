import tkinter as tk
import time
import os
import psutil
from tkinter import ttk, messagebox, filedialog
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from clases.cargador    import CargadorCSV
from clases.generador   import GeneradorPoblacion
from clases.evaluador   import EvaluadorAptitud
from clases.seleccionador import Seleccionador
from clases.cruce       import Cruce
from clases.mutador     import Mutador
from clases.algoritmo   import AlgoritmoGenetico
from clases.modelos     import Asignacion           # bloqueos


class HorarioApp:
    """Aplicación principal para generar y administrar horarios con un algoritmo genético."""

    # ─────────────────────────────── INIT ───────────────────────────────
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Generador de Horario")

        # ---------------------------  ESTADO  ---------------------------
        self.ultimas_asignaciones = None
        self.ultimo_reporte       = None
        self.faltantes_obl: list  = []
        self.faltantes_opt: list  = []
        self.cursos_activos:   set | None = None
        self.docentes_activos: set | None = None
        self.bloqueos: list[Asignacion]   = []   # asignaciones fijas

        # --------------------  PALETA DE COLORES  -----------------------
        self.colores_reporte = {
            "cursos"            : "#f9e79f",  "docentes"           : "#aed6f1",
            "salones"           : "#a9dfbf",  "asignaciones"       : "#d2b4de",
            "conflictos_docente": "#f5b7b1",  "conflictos_salon"   : "#f5b7b1",
            "conflictos_semestre":"#f5b7b1",  "cursos_faltantes"   : "#f5b7b1",
            "continuidad"       : "#aed6f1",  "bloques_seguidos"   : "#aed6f1",
            "aptitud_final"     : "#fad7a0",
            "iteraciones_optimas": "#d6eaf8",
            "tiempo_ejec": "#fdebd0", "porc_consecutivos": "#f4d03f",
            "memoria_usada": "#d4efdf"
        }
        self.orden_superior = ["cursos","docentes","salones","asignaciones"]
        self.orden_inferior = [
            "conflictos_docente","conflictos_salon","conflictos_semestre",
            "cursos_faltantes","continuidad","bloques_seguidos","porc_consecutivos","aptitud_final","iteraciones_optimas","tiempo_ejec","memoria_usada"
        ]

        # ------------------  SELECTOR DE SEMESTRE  ----------------------
        self.semestre_var = tk.StringVar(value="par")
        tk.Label(root, text="Selecciona el semestre:").pack(pady=8)
        tk.Radiobutton(root, text="Semestres Pares"   , variable=self.semestre_var, value="par" ).pack()
        tk.Radiobutton(root, text="Semestres Impares", variable=self.semestre_var, value="impar").pack()

        # -------------------  PARÁMETROS GA  ----------------------------
        param_frame = tk.LabelFrame(root, text="Parámetros del algoritmo", padx=6, pady=4)
        param_frame.pack(pady=10, fill="x")

        self.pop_var   = tk.IntVar(value=50)
        self.gen_var   = tk.IntVar(value=100)
        self.mut_var   = tk.DoubleVar(value=0.20)
        self.tor_var   = tk.IntVar(value=3)
        self.meta_var = tk.DoubleVar(value=0.0)

        ttk.Label(param_frame, text="Población:").grid(row=0, column=0, sticky="e")
        ttk.Spinbox(param_frame, from_=10, to=500, width=6, textvariable=self.pop_var).grid(row=0, column=1, padx=4)

        ttk.Label(param_frame, text="Generaciones:").grid(row=0, column=2, sticky="e")
        ttk.Spinbox(param_frame, from_=10, to=2000, width=6, textvariable=self.gen_var).grid(row=0, column=3, padx=4)

        ttk.Label(param_frame, text="Prob. mutación:").grid(row=1, column=0, sticky="e", pady=2)
        ttk.Spinbox(param_frame, from_=0.0, to=1.0, increment=0.05, width=6,
                    textvariable=self.mut_var, format="%.2f").grid(row=1, column=1, padx=4, pady=2)

        ttk.Label(param_frame, text="Torneo k:").grid(row=1, column=2, sticky="e", pady=2)
        ttk.Spinbox(param_frame, from_=2, to=10, width=6, textvariable=self.tor_var).grid(row=1, column=3, padx=4, pady=2)

        ttk.Label(param_frame, text="Aptitud meta:").grid(row=2, column=0, sticky="e", pady=2)
        ttk.Spinbox(param_frame, from_=0.0, to=1_000_000, increment=1.0, width=8,
            textvariable=self.meta_var, format="%.1f").grid(row=2, column=1, padx=4, pady=2)

        # ----------------------  BOTÓN GENERAR  -------------------------
        self.generar_button = tk.Button(root, text="Generar Horario", command=self.generar_horario)
        self.generar_button.pack(pady=10)

        # ------------------  BOTONES SECUNDARIOS  -----------------------
        boton_frame = tk.Frame(root); boton_frame.pack(pady=(0, 15))

        self.btn_seleccion = tk.Button(boton_frame, text="Seleccionar cursos / docentes", command=self.ventana_seleccion)
        self.btn_bloqueo   = tk.Button(boton_frame, text="Asignar manualmente",          command=self.ventana_bloqueo)
        self.btn_html      = tk.Button(boton_frame, text="Exportar a HTML", state="disabled", command=self.exportar_html)
        self.btn_pdf       = tk.Button(boton_frame, text="Exportar a PDF" , state="disabled", command=self.exportar_pdf)
        self.btn_faltantes = tk.Button(boton_frame, text="Cursos faltantes", state="disabled", command=self.mostrar_cursos_faltantes)
        self.btn_grafica  = tk.Button(
        boton_frame, text="Ver evolución", state="disabled",
        command=self.mostrar_grafica)
        self.btn_csv = tk.Button(boton_frame, text="Exportar Conflictos",
                         state="disabled", command=self.exportar_csv)

        for b in (self.btn_seleccion, self.btn_bloqueo, self.btn_html,
                self.btn_pdf, self.btn_faltantes, self.btn_grafica,self.btn_csv):
            b.pack(side="left", padx=4)

        # ---------------------  FRAME DE REPORTES  ----------------------
        self.report_frame = tk.Frame(root); self.report_frame.pack(pady=8)

        # ---------------------  TABLA (Canvas)  -------------------------
        self.canvas = tk.Canvas(root)
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.tabla_frame = tk.Frame(self.canvas)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0, 0), window=self.tabla_frame, anchor="nw")
        self.tabla_frame.bind("<Configure>", self.on_frame_configure)

    # ─────────────────────────────── CORE ───────────────────────────────
    def generar_horario(self):
        semestre = self.semestre_var.get()
        asignaciones, reporte = self.generar_datos_horario(semestre)

        # filtra duplicados / conflictos con bloqueos
        cod_bloq   = {b.curso.codigo for b in self.bloqueos}
        clash_doc  = {(b.docente.registro, b.hora) for b in self.bloqueos}
        clash_room = {(b.salon.id, b.hora)         for b in self.bloqueos}

        asignaciones = [
            a for a in asignaciones
            if a.curso.codigo not in cod_bloq
            and (a.docente.registro, a.hora) not in clash_doc
            and (a.salon.id,       a.hora)   not in clash_room
        ]
        asignaciones = self.bloqueos + asignaciones

        self.ultimas_asignaciones = asignaciones
        self.ultimo_reporte       = reporte
        self.mostrar_reportes(reporte)
        self.mostrar_horario(asignaciones)

        for b in (self.btn_html, self.btn_pdf, self.btn_faltantes):
            b.config(state="normal")

    def generar_datos_horario(self, semestre):
        # -------- carga de datos --------
        cursos     = self.cargar_cursos()
        docentes   = self.cargar_docentes()
        salones    = self.cargar_salones()
        relaciones = self.cargar_relaciones()

        # -------- filtros por selección del usuario --------
        if self.cursos_activos   is not None:
            cursos   = [c for c in cursos   if c.codigo   in self.cursos_activos]
        if self.docentes_activos is not None:
            docentes = [d for d in docentes if d.registro in self.docentes_activos]

        codigos_cursos = {c.codigo   for c in cursos}
        registros_doc  = {d.registro for d in docentes}
        relaciones = [r for r in relaciones if r.curso_codigo in codigos_cursos and r.docente_id in registros_doc]

        # -------- filtro por semestre --------
        sem_filtrados = [2,4,6,8,10] if semestre == "par" else [1,3,5,7,9]
        cursos_filtrados = [c for c in cursos if c.semestre in sem_filtrados]

        # -------- crear GA --------
        generador = GeneradorPoblacion(cursos_filtrados, docentes, salones, relaciones, bloqueos=self.bloqueos)
        evaluador = EvaluadorAptitud(cursos_filtrados)
        cruce     = Cruce(bloqueos=self.bloqueos)
        mutador   = Mutador(generador.docentes_por_curso, salones, bloqueos=self.bloqueos)

        ga = AlgoritmoGenetico(
            evaluador=evaluador,
            seleccionador=Seleccionador(),
            cruce=cruce,
            mutador=mutador,
            generador=generador,
        )

        # parámetros del usuario
        generaciones = self.gen_var.get()
        tam_pob      = self.pop_var.get()
        torneo_k     = self.tor_var.get()
        prob_mut     = self.mut_var.get()
        apt_meta     = self.meta_var.get()

        t0 = time.perf_counter()
        mejor = ga.ejecutar(generaciones=generaciones,
                    tamaño_pob=tam_pob,
                    torneo_k=torneo_k,
                    prob_mutacion=prob_mut,
                    aptitud_meta=apt_meta)
        t1 = time.perf_counter()
        self.exec_time = t1 - t0
        process = psutil.Process(os.getpid())
        self.memory_used = round(process.memory_info().rss / (1024 * 1024), 2)
        self.gen_optima = ga.gen_optima
        self.hist_aptitud   = ga.historial
        self.conflicts_hist = ga.conflictos_por_gen
        self.btn_csv.config(state="normal")
        self.hist_aptitud = ga.historial
        self.btn_grafica.config(state="normal")
        asignaciones = mejor.asignaciones

        # -------- faltantes --------
        asignados = {a.curso.codigo for a in asignaciones} | {b.curso.codigo for b in self.bloqueos}
        self.faltantes_obl = [c for c in cursos_filtrados if c.tipo=="obligatorio" and c.codigo not in asignados]
        self.faltantes_opt = [c for c in cursos_filtrados if c.tipo=="optativo"   and c.codigo not in asignados]
        total_obl = sum(1 for c in cursos_filtrados if c.tipo == "obligatorio")
        reporte = self.generar_reporte(cursos_filtrados, docentes, salones,
                                       self.bloqueos + asignaciones, evaluador)
        return asignaciones, reporte


    # ──────────────────────────── SELECCIÓN GUI ─────────────────────────
    def ventana_seleccion(self):
        top = tk.Toplevel(self.root)
        top.title("Seleccionar cursos y docentes")
        top.grab_set()

        notebook = ttk.Notebook(top)
        frm_cursos = ttk.Frame(notebook)
        frm_docentes = ttk.Frame(notebook)
        notebook.add(frm_cursos, text="Cursos")
        notebook.add(frm_docentes, text="Docentes")
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # ---- lista de cursos -----------------------------------------
        cursos = sorted(self.cargar_cursos(), key=lambda c: (c.carrera, c.semestre, c.codigo))
        self.vars_cursos = {}
        canvas_c = tk.Canvas(frm_cursos)
        scr_c = tk.Scrollbar(frm_cursos, orient="vertical", command=canvas_c.yview)
        canvas_c.configure(yscrollcommand=scr_c.set)
        scr_c.pack(side="right", fill="y")
        canvas_c.pack(side="left", fill="both", expand=True)
        cont_c = tk.Frame(canvas_c)
        canvas_c.create_window((0, 0), window=cont_c, anchor="nw")
        cont_c.bind("<Configure>", lambda e: canvas_c.configure(scrollregion=canvas_c.bbox("all")))

        for i, c in enumerate(cursos):
            sel = True if self.cursos_activos is None else c.codigo in self.cursos_activos
            var = tk.BooleanVar(value=sel)
            self.vars_cursos[c.codigo] = var
            txt = f"{c.codigo} | {c.nombre} | Sem.{c.semestre} | {c.carrera}"
            tk.Checkbutton(cont_c, text=txt, variable=var, anchor="w").grid(row=i, column=0, sticky="w")

        # ---- lista de docentes ---------------------------------------
        docentes = sorted(self.cargar_docentes(), key=lambda d: d.nombre)
        self.vars_docentes = {}
        canvas_d = tk.Canvas(frm_docentes)
        scr_d = tk.Scrollbar(frm_docentes, orient="vertical", command=canvas_d.yview)
        canvas_d.configure(yscrollcommand=scr_d.set)
        scr_d.pack(side="right", fill="y")
        canvas_d.pack(side="left", fill="both", expand=True)
        cont_d = tk.Frame(canvas_d)
        canvas_d.create_window((0, 0), window=cont_d, anchor="nw")
        cont_d.bind("<Configure>", lambda e: canvas_d.configure(scrollregion=canvas_d.bbox("all")))

        for i, d in enumerate(docentes):
            sel = True if self.docentes_activos is None else d.registro in self.docentes_activos
            var = tk.BooleanVar(value=sel)
            self.vars_docentes[d.registro] = var
            txt = f"{d.registro} | {d.nombre}"
            tk.Checkbutton(cont_d, text=txt, variable=var, anchor="w").grid(row=i, column=0, sticky="w")

        # ---- botones aceptar / cancelar ------------------------------
        btn_f = tk.Frame(top)
        btn_f.pack(pady=8)
        tk.Button(btn_f, text="Aceptar", width=12, command=lambda: self._guardar_seleccion(top)).pack(side="left", padx=6)
        tk.Button(btn_f, text="Cancelar", width=12, command=top.destroy).pack(side="left", padx=6)

    def _guardar_seleccion(self, ventana: tk.Toplevel):
        self.cursos_activos = {cod for cod, var in self.vars_cursos.items() if var.get()}
        self.docentes_activos = {reg for reg, var in self.vars_docentes.items() if var.get()}
        ventana.destroy()
        messagebox.showinfo("Selección guardada", "Los cursos y docentes seleccionados se usarán en la próxima generación.")

    # ──────────────────────── DIÁLOGO DE ASIGNACIÓN MANUAL ─────────────────────────
    def ventana_bloqueo(self):
        cursos = sorted(self.cargar_cursos(), key=lambda c: c.codigo)
        docentes = sorted(self.cargar_docentes(), key=lambda d: d.nombre)
        salones = sorted(self.cargar_salones(), key=lambda s: s.nombre)
        horas = self.cargar_horas()  # helper

        top = tk.Toplevel(self.root)
        top.title("Asignar curso manualmente")
        top.grab_set()

        tk.Label(top, text="Curso:").grid(row=0, column=0, sticky="e", pady=4, padx=4)
        tk.Label(top, text="Docente:").grid(row=1, column=0, sticky="e", pady=4, padx=4)
        tk.Label(top, text="Salón:").grid(row=2, column=0, sticky="e", pady=4, padx=4)
        tk.Label(top, text="Hora:").grid(row=3, column=0, sticky="e", pady=4, padx=4)

        cb_curso   = ttk.Combobox(top, values=[f"{c.codigo} – {c.nombre}" for c in cursos], state="readonly", width=45)
        cb_docente = ttk.Combobox(top, values=[f"{d.registro} – {d.nombre}" for d in docentes], state="readonly", width=45)
        cb_salon   = ttk.Combobox(top, values=[f"{s.id} – {s.nombre}" for s in salones], state="readonly", width=45)
        cb_hora    = ttk.Combobox(top, values=horas, state="readonly", width=10)

        cb_curso.grid(row=0, column=1, pady=4, padx=4)
        cb_docente.grid(row=1, column=1, pady=4, padx=4)
        cb_salon.grid(row=2, column=1, pady=4, padx=4)
        cb_hora.grid(row=3, column=1, pady=4, padx=4)

        def guardar():
            if not all((cb_curso.get(), cb_docente.get(), cb_salon.get(), cb_hora.get())):
                messagebox.showwarning("Datos incompletos", "Selecciona curso, docente, salón y hora.")
                return
            curso = next(c for c in cursos if c.codigo in cb_curso.get().split(" – ")[0])
            docente = next(d for d in docentes if d.registro in cb_docente.get().split(" – ")[0])
            salon = next(s for s in salones if str(s.id) == cb_salon.get().split(" – ")[0])
            hora = cb_hora.get()

            # comprobar duplicados
            for a in self.bloqueos:
                if a.curso.codigo == curso.codigo:
                    messagebox.showerror("Ya existe", "Ese curso ya tiene un bloqueo definido.")
                    return
                if (a.docente.registro, a.hora) == (docente.registro, hora):
                    messagebox.showerror("Conflicto", "Ese docente ya está bloqueado a esa hora.")
                    return
                if (a.salon.id, a.hora) == (salon.id, hora):
                    messagebox.showerror("Conflicto", "Ese salón ya está bloqueado a esa hora.")
                    return

            self.bloqueos.append(Asignacion(curso, docente, salon, hora))
            top.destroy()
            messagebox.showinfo("Bloqueo añadido", "La asignación manual se respetará al generar el horario.")

        ttk.Button(top, text="Guardar", command=guardar).grid(row=4, column=0, columnspan=2, pady=8)

    # helper
    def cargar_horas(self):
        from clases.generador import HORAS_DISPONIBLES
        return HORAS_DISPONIBLES

    # ──────────────────────────────────────  REPORTES  ──────────────────────────────────────
    def _bloque_reporte(self, parent, clave, valor):
        nombres = {
            "cursos": "Cursos",
            "docentes": "Docentes",
            "salones": "Salones",
            "asignaciones": "Asignaciones",
            "conflictos_docente": "Conf. docente",
            "conflictos_salon": "Conf. salón",
            "conflictos_semestre": "Conf. oblig.",
            "cursos_faltantes": "Oblig. falt.",
            "continuidad": "Bloques cont.",
            "bloques_seguidos": "Bloques seg.",
            "aptitud_final": "Aptitud",
            "iteraciones_optimas": "Iterac. óptima",
            "tiempo_ejec": "Tiempo (s)",
            "porc_consecutivos": "Consec. (%)",
            "memoria_usada": "Memoria (MB)"
        }
        tk.Label(
            parent,
            text=f"{nombres[clave]}\n{valor}",
            width=14,
            height=3,
            bg=self.colores_reporte.get(clave, "white"),
            relief="ridge",
            borderwidth=2,
        ).pack(side="left", padx=2)

    def mostrar_reportes(self, rep):
        for w in self.report_frame.winfo_children():
            w.destroy()

        tk.Label(self.report_frame, text="Datos cargados:", font=("Helvetica", 10, "bold")).pack(fill="x")
        fila1 = tk.Frame(self.report_frame)
        fila1.pack(pady=(0, 4))
        for k in self.orden_superior:
            self._bloque_reporte(fila1, k, rep[k])

        tk.Label(self.report_frame, text="Reporte de aptitud:", font=("Helvetica", 10, "bold")).pack(
            fill="x", pady=(6, 0)
        )
        fila2 = tk.Frame(self.report_frame)
        fila2.pack(pady=(0, 2))
        for k in self.orden_inferior:
            self._bloque_reporte(fila2, k, rep[k])

    def generar_reporte(self, cursos, docentes, salones, asignaciones, ev):
        total_obl = sum(1 for c in cursos if c.tipo == "obligatorio")
        consec = len(ev.reporte.get("cursos_consecutivos_unicos", set()))
        porc = round((consec / total_obl) * 100, 1) if total_obl else 0.0
        return {
            "cursos": len(cursos),
            "docentes": len(docentes),
            "salones": len(salones),
            "asignaciones": len(asignaciones),
            "conflictos_docente": ev.reporte["conflictos_docente"],
            "conflictos_salon": ev.reporte["conflictos_salon"],
            "conflictos_semestre": ev.reporte["conflictos_semestre"],
            "cursos_faltantes": ev.reporte["cursos_faltantes"],
            "continuidad": ev.reporte["continuidad_bloques"],
            "bloques_seguidos": ev.reporte["bloques_seguidos"],
            "aptitud_final": ev.reporte["aptitud_final"],
            "iteraciones_optimas": self.gen_optima,
            "tiempo_ejec": round(self.exec_time, 3),
            "porc_consecutivos": porc,
            "memoria_usada": self.memory_used
        }

    # ──────────────────────────────────────  TABLA HORARIO  ──────────────────────────────────────
    def mostrar_horario(self, horarios):
        for w in self.tabla_frame.winfo_children():
            w.destroy()

        horas = sorted({a.hora for a in horarios})
        salones = sorted({a.salon.nombre for a in horarios})

        for i, h in enumerate(["Hora"] + salones):
            tk.Label(self.tabla_frame, text=h, relief="solid", width=35, height=2).grid(row=0, column=i)

        mapa = {
            (a.hora, a.salon.nombre): (
                f"{a.curso.nombre}\n{a.docente.nombre}\n"
                f"Sem. {a.curso.semestre} | {a.curso.carrera} | Sec. {a.curso.seccion}\n"
                f"Tipo: {a.curso.tipo.capitalize()}"
            )
            for a in horarios
        }

        for i, hora in enumerate(horas, 1):
            tk.Label(self.tabla_frame, text=hora, relief="solid", width=35, height=5).grid(row=i, column=0)
            for j, salon in enumerate(salones, 1):
                color = self.asignar_color(hora, salon, horarios)
                tk.Label(
                    self.tabla_frame,
                    text=mapa.get((hora, salon), ""),
                    relief="solid",
                    width=35,
                    height=5,
                    bg=color,
                    fg="black",
                ).grid(row=i, column=j)

    def asignar_color(self, hora, salon, horarios):
        for a in horarios:
            if a.hora == hora and a.salon.nombre == salon:
                return {
                    "Ingeniería en Sistemas": "lightblue",
                    "Ingeniería Civil": "lightgreen",
                    "Ingeniería Industrial": "lightyellow",
                    "Ingeniería Mecánica": "lightcoral",
                }.get(a.curso.carrera, "white")
        return "white"

    # ──────────────────────────────────────  CURSOS FALTANTES  ──────────────────────────────────────
    def mostrar_cursos_faltantes(self):
        if not (self.faltantes_obl or self.faltantes_opt):
            messagebox.showinfo("Cursos faltantes", "¡No hay cursos faltantes!")
            return

        top = tk.Toplevel(self.root)
        top.title("Cursos faltantes")

        # ── canvas + scrollbar ───────────────────────────────────────
        canvas = tk.Canvas(top, borderwidth=0)
        vsb = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        contenedor = tk.Frame(canvas)
        canvas.create_window((0, 0), window=contenedor, anchor="nw")

        # actualizar región scrollable
        contenedor.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ── encabezados ─────────────────────────────────────────────
        headers = ["Código", "Nombre", "Carrera", "Semestre", "Tipo", "Sección"]
        for i, h in enumerate(headers):
            tk.Label(contenedor, text=h, relief="ridge", width=18, bg="#d5d8dc",fg="black").grid(row=0, column=i, sticky="nsew")

        fila = 1
        for c in self.faltantes_obl:                    # obligatorios primero
            self._fila_curso(contenedor, fila, c, "#f9ebea")
            fila += 1
        for c in self.faltantes_opt:                    # luego optativos
            self._fila_curso(contenedor, fila, c, "#e8f8f5")
            fila += 1

        for i in range(len(headers)):                   # columnas expandibles
            contenedor.grid_columnconfigure(i, weight=1)

    def _fila_curso(self, parent, fila, curso, color):
        datos = [
            curso.codigo,
            curso.nombre,
            curso.carrera,
            curso.semestre,
            curso.tipo.capitalize(),
            curso.seccion,
        ]
        for col, dato in enumerate(datos):
            tk.Label(parent, text=dato, bg=color, relief="ridge", width=18, wraplength=150, fg="black").grid(
                row=fila, column=col, sticky="nsew"
            )

    # ──────────────────────────────────────  EXPORTAR HTML  ──────────────────────────────────────
    def exportar_html(self):
        if not self.ultimas_asignaciones:
            return
        file = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
        if not file:
            return

        horas = sorted({a.hora for a in self.ultimas_asignaciones})
        salones = sorted({a.salon.nombre for a in self.ultimas_asignaciones})
        mapa = {
            (a.hora, a.salon.nombre): (
                f"{a.curso.nombre}<br>{a.docente.nombre}<br>"
                f"Sem.{a.curso.semestre} | {a.curso.carrera} | Sec.{a.curso.seccion}<br>"
                f"<b>{a.curso.tipo.capitalize()}</b>"
            )
            for a in self.ultimas_asignaciones
        }

        html = "<html><head><meta charset='utf-8'><title>Horario</title>"
        html += (
            "<style>table{border-collapse:collapse}"
            "td,th{border:1px solid #666;padding:4px;text-align:center}</style></head><body>"
        )

        html += "<h3>Datos cargados</h3><table><tr>"
        for k in self.orden_superior:
            html += f"<td bgcolor='{self.colores_reporte[k]}'>{k.capitalize()}<br>{self.ultimo_reporte[k]}</td>"
        html += "</tr></table><h3>Reporte de aptitud</h3><table><tr>"
        for k in self.orden_inferior:
            html += (
                f"<td bgcolor='{self.colores_reporte[k]}'>{k.replace('_',' ').title()}<br>{self.ultimo_reporte[k]}</td>"
            )
        html += "</tr></table><br>"

        html += "<table><tr><th>Hora</th>" + "".join(f"<th>{s}</th>" for s in salones) + "</tr>"
        for h in horas:
            html += f"<tr><td>{h}</td>"
            for s in salones:
                html += f"<td>{mapa.get((h, s), '')}</td>"
            html += "</tr>"
        html += "</table></body></html>"

        with open(file, "w", encoding="utf-8") as f:
            f.write(html)
        messagebox.showinfo("Exportar HTML", f"Horario guardado en:\n{file}")

    # ──────────────────────────────────────  EXPORTAR PDF  ──────────────────────────────────────
    def exportar_pdf(self):
        if not self.ultimas_asignaciones:
            return
        file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not file:
            return

        doc = SimpleDocTemplate(file, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elems = []

        # bloques de reporte
        datos1 = [[k.capitalize(), self.ultimo_reporte[k]] for k in self.orden_superior]
        tabla1 = Table(datos1, colWidths=[120, 60])
        tabla1.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke), ("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
        elems.append(tabla1)
        elems.append(Spacer(1, 5))

        datos2 = [[k.replace("_", " ").title(), self.ultimo_reporte[k]] for k in self.orden_inferior]
        tabla2 = Table(datos2, colWidths=[150, 60])
        tabla2.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke), ("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
        elems.append(tabla2)
        elems.append(Spacer(1, 10))

        # tabla horario
        horas = sorted({a.hora for a in self.ultimas_asignaciones})
        salones = sorted({a.salon.nombre for a in self.ultimas_asignaciones})
        header = ["Hora"] + salones
        datos_h = [header]
        mapa = {
            (a.hora, a.salon.nombre): (
                f"{a.curso.nombre}\n{a.docente.nombre}\n"
                f"Sem. {a.curso.semestre} | {a.curso.carrera} | Sec. {a.curso.seccion}\n"
                f"{a.curso.tipo.capitalize()}"
            )
            for a in self.ultimas_asignaciones
        }
        for h in horas:
            datos_h.append([h] + [mapa.get((h, s), "") for s in salones])

        tabla_h = Table(datos_h, repeatRows=1, colWidths=[50] + [120] * len(salones))
        tabla_h.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 6),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ]
            )
        )
        elems.append(tabla_h)

        doc.build(elems)
        messagebox.showinfo("Exportar PDF", f"Horario guardado en:\n{file}")

    def exportar_csv(self):
        if not hasattr(self, "hist_aptitud"):
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")])
        if not file:
            return
        with open(file, "w", encoding="utf-8") as f:
            f.write("generacion,aptitud_mejor,conflictos\n")
            for i, (apt, conf) in enumerate(zip(self.hist_aptitud,
                                                self.conflicts_hist)):
                f.write(f"{i},{apt},{conf}\n")
        messagebox.showinfo("CSV", f"Datos guardados en:\n{file}")

    def mostrar_grafica(self):
        if not hasattr(self, "hist_aptitud"):
            return
        top = tk.Toplevel(self.root)
        top.title("Evolución de la aptitud")

        fig = Figure(figsize=(6, 4), dpi=100)
        ax  = fig.add_subplot(111)
        ax.plot(self.hist_aptitud, marker="o")
        ax.set_xlabel("Generación")
        ax.set_ylabel("Aptitud")
        ax.set_title("Mejor aptitud por generación")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    # ──────────────────────────────────────  UTILS  ──────────────────────────────────────
    def on_frame_configure(self, _=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def cargar_cursos(self):
        return CargadorCSV.cargar_cursos("data/cursos.csv")

    def cargar_docentes(self):
        return CargadorCSV.cargar_docentes("data/docentes.csv")

    def cargar_salones(self):
        return CargadorCSV.cargar_salones("data/salones.csv")

    def cargar_relaciones(self):
        return CargadorCSV.cargar_relaciones("data/relaciones.csv")


# ────────────────────────────────────────────  MAIN  ────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.option_add("*Font", ("Helvetica", 9))   # usa el mismo root
    app = HorarioApp(root)
    root.mainloop()
