from typing import List
from collections import defaultdict
import random

class Curso:
    def __init__(self, codigo, nombre, carrera, semestre, tipo, seccion):
        self.codigo = codigo
        self.nombre = nombre
        self.carrera = carrera
        self.semestre = int(semestre)
        self.tipo = tipo.lower()
        self.seccion = seccion

class Docente:
    def __init__(self, nombre, registro, entrada, salida):
        self.nombre = nombre
        self.registro = registro
        self.entrada = entrada
        self.salida = salida

class Salon:
    def __init__(self, nombre, id_):
        self.nombre = nombre
        self.id = id_

class RelacionDocenteCurso:
    def __init__(self, docente_id, curso_codigo):
        self.docente_id = docente_id
        self.curso_codigo = curso_codigo

class Asignacion:
    def __init__(self, curso: Curso, docente: Docente, salon: Salon, hora: str):
        self.curso = curso
        self.docente = docente
        self.salon = salon
        self.hora = hora

class Individuo:
    def __init__(self, asignaciones: List[Asignacion]):
        self.asignaciones = asignaciones
        self.aptitud = None
