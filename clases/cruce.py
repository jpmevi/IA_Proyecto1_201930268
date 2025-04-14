import random
from typing import List, Optional
from .modelos import Individuo, Asignacion


class Cruce:
    """
    Cruce de un punto que **respeta** las asignaciones fijas (bloqueos):
    1. Elimina cualquier asignación que entre en conflicto con un bloqueo.
    2. Vuelve a insertar todas las asignaciones bloqueadas.
    """

    def __init__(self, bloqueos: Optional[List[Asignacion]] = None):
        self.bloqueos: List[Asignacion] = bloqueos or []

    # ------------------------------------------------------------------
    def cruzar(self, padre1: Individuo, padre2: Individuo) -> Individuo:
        # ── cruce de un punto (simple) ────────────────────────────────
        corte = random.randint(1, len(padre1.asignaciones) - 1)
        hijo_asig = padre1.asignaciones[:corte] + padre2.asignaciones[corte:]

        # ── 1) quitar todo lo que choque con bloqueos ─────────────────
        cod_bloq   = {b.curso.codigo for b in self.bloqueos}
        clash_doc  = {(b.docente.registro, b.hora) for b in self.bloqueos}
        clash_room = {(b.salon.id,       b.hora) for b in self.bloqueos}

        hijo_asig = [
            a for a in hijo_asig
            if a.curso.codigo not in cod_bloq
            and (a.docente.registro, a.hora) not in clash_doc
            and (a.salon.id, a.hora)        not in clash_room
        ]

        # ── 2) volver a insertar los bloqueos ─────────────────────────
        hijo_asig.extend(self.bloqueos)

        return Individuo(hijo_asig)
