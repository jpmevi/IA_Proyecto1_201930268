import random
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional
from .modelos import Individuo, Asignacion
from .generador import HORAS_DISPONIBLES


class Mutador:
    """
    Mutador que evita tocar las asignaciones fijas (bloqueos).
    Puede mutar hora, docente y salón con probabilidad `prob_mutacion`.
    """

    def __init__(
        self,
        docentes_por_curso: Dict[str, List],
        salones: List,
        bloqueos: Optional[List[Asignacion]] = None,
    ):
        self.docentes_por_curso = docentes_por_curso
        self.salones = salones
        self.bloqueos: List[Asignacion] = bloqueos or []
        # ids de las asignaciones bloqueadas para reconocerlas rápido
        self._ids_bloqueados: Set[int] = {id(a) for a in self.bloqueos}

    # ------------------------------------------------------------------
    def mutar(self, individuo: Individuo, prob_mutacion: float = 0.2) -> None:
        # ── construir tablas de ocupación actuales ────────────────────
        horarios_docente: Dict[str, Set[str]] = {}
        horarios_salon: Dict[int, Set[str]] = {}
        horarios_semestre: Dict[Tuple[str, int], Set[str]] = defaultdict(set)

        for a in individuo.asignaciones:
            horarios_docente.setdefault(a.docente.registro, set()).add(a.hora)
            horarios_salon.setdefault(a.salon.id, set()).add(a.hora)
            if a.curso.tipo == "obligatorio":
                horarios_semestre[(a.curso.carrera, a.curso.semestre)].add(a.hora)

        # ── recorrer asignaciones (excepto bloqueadas) ────────────────
        for asignacion in individuo.asignaciones:
            if id(asignacion) in self._ids_bloqueados:
                continue  # ¡no tocar!

            # ---------- mutar hora ----------
            if random.random() < prob_mutacion:
                key_sem = (asignacion.curso.carrera, asignacion.curso.semestre)
                posibles_horas = [
                    h for h in HORAS_DISPONIBLES
                    if h != asignacion.hora
                    and h not in horarios_docente.get(asignacion.docente.registro, set())
                    and h not in horarios_salon.get(asignacion.salon.id, set())
                    and (
                        asignacion.curso.tipo != "obligatorio"
                        or h not in horarios_semestre[key_sem]
                    )
                ]
                if posibles_horas:
                    nueva_hora = random.choice(posibles_horas)
                    # actualizar tablas
                    horarios_docente[asignacion.docente.registro].discard(asignacion.hora)
                    horarios_docente[asignacion.docente.registro].add(nueva_hora)
                    horarios_salon[asignacion.salon.id].discard(asignacion.hora)
                    horarios_salon[asignacion.salon.id].add(nueva_hora)
                    if asignacion.curso.tipo == "obligatorio":
                        horarios_semestre[key_sem].discard(asignacion.hora)
                        horarios_semestre[key_sem].add(nueva_hora)
                    asignacion.hora = nueva_hora

            # ---------- mutar docente ----------
            if random.random() < prob_mutacion:
                posibles_docentes = self.docentes_por_curso.get(asignacion.curso.codigo, [])
                if posibles_docentes:
                    nuevo_docente = random.choice(posibles_docentes)
                    if asignacion.hora not in horarios_docente.get(nuevo_docente.registro, set()):
                        horarios_docente[asignacion.docente.registro].discard(asignacion.hora)
                        asignacion.docente = nuevo_docente
                        horarios_docente.setdefault(nuevo_docente.registro, set()).add(asignacion.hora)

            # ---------- mutar salón ----------
            if random.random() < prob_mutacion:
                salones_disponibles = [
                    s for s in self.salones
                    if asignacion.hora not in horarios_salon.get(s.id, set())
                ]
                if salones_disponibles:
                    nuevo_salon = random.choice(salones_disponibles)
                    horarios_salon[asignacion.salon.id].discard(asignacion.hora)
                    asignacion.salon = nuevo_salon
                    horarios_salon.setdefault(nuevo_salon.id, set()).add(asignacion.hora)
