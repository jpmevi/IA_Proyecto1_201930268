import string
from collections import defaultdict


class AlgoritmoGenetico:
    def __init__(self, evaluador, seleccionador, cruce, mutador, generador):
        self.evaluador     = evaluador
        self.seleccionador = seleccionador
        self.cruce         = cruce
        self.mutador       = mutador
        self.generador     = generador
        self.historial           = []
        self.conflictos_por_gen  = []
        self.gen_optima         = 0

    def _snapshot(self, mejor_ind):
        """Guarda aptitud y número total de conflictos del individuo."""
        self.historial.append(mejor_ind.aptitud)
        rep = self.evaluador.reporte
        total_conf = (rep["conflictos_docente"] + rep["conflictos_salon"] +
                      rep["conflictos_semestre"] + rep["cursos_faltantes"])
        self.conflictos_por_gen.append(total_conf)
    # ─────────────────────────────────────────────────────────────
    def ejecutar(self, *,
                 generaciones: int,
                 tamaño_pob: int,
                 torneo_k: int = 3,
                 prob_mutacion: float = 0.2,
                 aptitud_meta: float | None = None):
        """Corre el GA y devuelve el mejor individuo encontrado.
        Se detiene antes si se alcanza aptitud_meta (si se proporciona)."""
        # 1) población inicial
        poblacion = self.generador.generar_poblacion(tamaño_pob)
        for ind in poblacion:
            self.evaluador.evaluar(ind)

        mejor = max(poblacion, key=lambda i: i.aptitud)
        self._snapshot(mejor)
        self.gen_optima = 0

        self.historial: list[float] = [mejor.aptitud]   # mejor de la gen‑0
        if aptitud_meta is not None and mejor.aptitud >= aptitud_meta:
            self._asignar_secciones(mejor)
            return mejor

        # 2) ciclo evolutivo
        for g in range(generaciones):
            nueva_pob = [mejor]                       # elitismo opcional

            while len(nueva_pob) < tamaño_pob:
                p1 = self.seleccionador.seleccionar(poblacion, torneo_k)
                p2 = self.seleccionador.seleccionar(poblacion, torneo_k)
                hijo = self.cruce.cruzar(p1, p2)
                self.mutador.mutar(hijo, prob_mutacion=prob_mutacion)
                self.evaluador.evaluar(hijo)
                nueva_pob.append(hijo)

            poblacion = nueva_pob

            cand = max(poblacion, key=lambda i: i.aptitud)
            if cand.aptitud > mejor.aptitud:
                mejor = cand
                self.gen_optima = g
            self._snapshot(mejor)

            self.historial.append(mejor.aptitud)
            # parada temprana
            if aptitud_meta is not None and mejor.aptitud >= aptitud_meta:
                break

        self._asignar_secciones(mejor)
        return mejor

    # ─────────────────────────────────────────────────────────────
    def _asignar_secciones(self, individuo):
        conteo = defaultdict(int)
        for a in individuo.asignaciones:
            key = a.curso.codigo
            conteo[key] += 1
            a.curso.seccion = string.ascii_uppercase[conteo[key] - 1]
