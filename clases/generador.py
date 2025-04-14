import random
from typing import List, Dict, Set, Tuple, Optional
from .modelos import (
    Curso,
    Docente,
    Salon,
    RelacionDocenteCurso,
    Asignacion,
    Individuo,
)

# ───────────────────────── HORAS DISPONIBLES ─────────────────────────
HORAS_DISPONIBLES: List[str] = []


def _generar_horas_disponibles() -> None:
    h, m = 13, 40  # 13:40 – 21:10 cada 50 min
    while h < 21 or (h == 21 and m <= 10):
        HORAS_DISPONIBLES.append(f"{h:02d}:{m:02d}")
        m += 50
        if m >= 60:
            h += 1
            m -= 60


_generar_horas_disponibles()

# ───────────────────────── GENERADOR DE POBLACIÓN ─────────────────────────
class GeneradorPoblacion:
    """Crea individuos (horarios) cumpliendo las restricciones duras mínimas."""

    def __init__(
        self,
        cursos: List[Curso],
        docentes: List[Docente],
        salones: List[Salon],
        relaciones: List[RelacionDocenteCurso],
        bloqueos: Optional[List[Asignacion]] = None,  # ← NUEVO
    ):
        self.cursos = cursos
        self.docentes = docentes
        self.salones = salones
        self.relaciones = relaciones
        self.bloqueos: List[Asignacion] = bloqueos or []  # lista (puede estar vacía)

        # mapa {codigo_curso: [docente1, docente2, …]}
        self.docentes_por_curso = self._mapear_docentes()

    # ───────────────────── helpers ─────────────────────
    def _mapear_docentes(self) -> Dict[str, List[Docente]]:
        """Devuelve un dict con los docentes disponibles para cada curso.
        Si una relación hace referencia a un docente filtrado, simplemente se ignora.
        """
        mapa: Dict[str, List[Docente]] = {}
        for r in self.relaciones:
            doc = next((d for d in self.docentes if d.registro == r.docente_id), None)
            if doc is None:
                continue  # docente desactivado
            mapa.setdefault(r.curso_codigo, []).append(doc)
        return mapa

    # ───────────────────── creación de individuos ─────────────────────
    def generar_individuo(self) -> Individuo:
        """Crea un Individuo respetando las asignaciones fijas (bloqueos)."""
        asignaciones: List[Asignacion] = list(self.bloqueos)  # copia

        # conjuntos ocupados a partir de los bloqueos
        ocup_docente: Set[Tuple[str, str]] = {(a.docente.registro, a.hora) for a in asignaciones}
        ocup_salon: Set[Tuple[int, str]] = {(a.salon.id, a.hora) for a in asignaciones}
        bloque_sem: Set[Tuple[str, int, str]] = {
            (a.curso.carrera, a.curso.semestre, a.hora)
            for a in asignaciones
            if a.curso.tipo == "obligatorio"
        }

        # cursos ya asignados por bloqueo
        cursos_ya_asignados = {a.curso.codigo for a in asignaciones}

        # obligatorios primero para priorizar su ubicación
        cursos_restantes = sorted(
            (c for c in self.cursos if c.codigo not in cursos_ya_asignados),
            key=lambda c: c.tipo == "optativo",
        )

        for curso in cursos_restantes:
            posibles_doc = self.docentes_por_curso.get(curso.codigo, [])
            if not posibles_doc:
                continue  # se penalizará después

            random.shuffle(posibles_doc)
            horas = HORAS_DISPONIBLES.copy()
            random.shuffle(horas)
            salones = self.salones.copy()
            random.shuffle(salones)

            for hora in horas:
                for docente in posibles_doc:
                    if (docente.registro, hora) in ocup_docente:
                        continue
                    for salon in salones:
                        if (salon.id, hora) in ocup_salon:
                            continue

                        # asignar
                        asignaciones.append(Asignacion(curso, docente, salon, hora))
                        ocup_docente.add((docente.registro, hora))
                        ocup_salon.add((salon.id, hora))
                        if curso.tipo == "obligatorio":
                            bloque_sem.add((curso.carrera, curso.semestre, hora))
                        hora = None  # rompe los bucles
                        break
                    if hora is None:
                        break
                if hora is None:
                    break

        random.shuffle(asignaciones)
        return Individuo(asignaciones)

    # ───────────────────── población inicial ─────────────────────
    def generar_poblacion(self, n: int) -> List[Individuo]:
        return [self.generar_individuo() for _ in range(n)]
