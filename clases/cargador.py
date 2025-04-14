import csv
from .modelos import Curso, Docente, Salon, RelacionDocenteCurso

class CargadorCSV:
    @staticmethod
    def cargar_cursos(path: str):
        cursos = []
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursos.append(Curso(
                    codigo=row["codigo"],
                    nombre=row["nombre"],
                    carrera=row["carrera"],
                    semestre=int(row["semestre"]),
                    tipo=row["tipo"],
                    seccion=row["seccion"]
                ))
        return cursos

    @staticmethod
    def cargar_docentes(path: str):
        docentes = []
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                docentes.append(Docente(
                    nombre=row["nombre"],
                    registro=row["registro"],
                    entrada=row["entrada"],
                    salida=row["salida"]
                ))
        return docentes

    @staticmethod
    def cargar_salones(path: str):
        salones = []
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                salones.append(Salon(
                    nombre=row["nombre"],
                    id_=row["id"]
                ))
        return salones

    @staticmethod
    def cargar_relaciones(path: str):
        relaciones = []
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                relaciones.append(RelacionDocenteCurso(
                    docente_id=row["registro"],
                    curso_codigo=row["codigo"]
                ))
        return relaciones
