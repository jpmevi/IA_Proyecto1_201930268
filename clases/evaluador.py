from .modelos import Individuo
from collections import defaultdict

class EvaluadorAptitud:
    def __init__(self, cursos_totales):
        self.reporte = {}
        self.cursos_totales = cursos_totales  # Cursos válidos (par o impar)

    def evaluar(self, individuo: Individuo):
        conflictos = 0
        continuidad = 0
        bloques_seguidos = 0

        self.reporte = {
            "conflictos_docente": 0,
            "conflictos_salon": 0,
            "conflictos_semestre": 0,
            "cursos_faltantes": 0,
            "continuidad_bloques": 0,
            "bloques_seguidos": 0,
            "aptitud_final": 0,
            "cursos_consecutivos_unicos": 0,
        }

        horario_docente = defaultdict(list)
        horario_salon = defaultdict(list)
        horario_semestre = defaultdict(list)
        cursos_asignados = set()

        for asignacion in individuo.asignaciones:
            cursos_asignados.add(asignacion.curso.codigo)

            horario_docente[asignacion.hora].append(asignacion.docente.registro)
            if horario_docente[asignacion.hora].count(asignacion.docente.registro) > 1:
                conflictos += 5
                self.reporte["conflictos_docente"] += 1

            horario_salon[asignacion.hora].append(asignacion.salon.id)
            if horario_salon[asignacion.hora].count(asignacion.salon.id) > 1:
                conflictos += 5
                self.reporte["conflictos_salon"] += 1

            if asignacion.curso.tipo == "obligatorio":
                key = (asignacion.curso.carrera, asignacion.curso.semestre, asignacion.hora)
                if key in horario_semestre:
                    conflictos += 10
                    self.reporte["conflictos_semestre"] += 1
                horario_semestre[key].append(asignacion.curso.codigo)

        codigos_obligatorios = {c.codigo for c in self.cursos_totales if c.tipo == "obligatorio"}
        faltantes = codigos_obligatorios - cursos_asignados
        if faltantes:
            conflictos += len(faltantes) * 15
            self.reporte["cursos_faltantes"] = len(faltantes)

        agrupados = defaultdict(list)
        self.reporte["cursos_consecutivos_unicos"] = set()
        for a in individuo.asignaciones:
            if a.curso.tipo == "obligatorio":
                key = (a.curso.carrera, a.curso.semestre)
                agrupados[key].append(a.hora)

        for horas in agrupados.values():
            minutos = sorted([self._hora_a_min(h) for h in horas])
            for i in range(len(minutos) - 1):
                delta = minutos[i+1] - minutos[i]
                if delta == 50:
                    continuidad += 1
                    bloques_seguidos += 5
                    self.reporte["cursos_consecutivos_unicos"].add(horas[i][1])
                    self.reporte["cursos_consecutivos_unicos"].add(horas[i+1][1])


        individuo.aptitud = -conflictos + continuidad + bloques_seguidos
        self.reporte["continuidad_bloques"] = continuidad
        self.reporte["bloques_seguidos"] = bloques_seguidos
        self.reporte["aptitud_final"] = individuo.aptitud
        return individuo.aptitud

    def imprimir_reporte(self):
        print("\n📊 Reporte de penalizaciones:")
        print(f"   - Conflictos de docente: {self.reporte['conflictos_docente']}")
        print(f"   - Conflictos de salón: {self.reporte['conflictos_salon']}")
        print(f"   - Conflictos entre obligatorios del mismo semestre: {self.reporte['conflictos_semestre']}")
        print(f"   - Cursos obligatorios faltantes: {self.reporte['cursos_faltantes']}")
        print(f"   - Bloques continuos ganados: {self.reporte['continuidad_bloques']}")
        print(f"   - Bloques seguidos (mismo semestre): {self.reporte['bloques_seguidos']}")
        print(f"   - Aptitud total: {self.reporte['aptitud_final']}")

    def _hora_a_min(self, hora: str):
        h, m = map(int, hora.split(":"))
        return h * 60 + m
