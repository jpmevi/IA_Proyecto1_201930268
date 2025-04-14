# 📘 Manual de Usuario

## Generador de Horarios Académicos con Algoritmo Genético

---

## 1. Introducción

La planificación de horarios académicos puede convertirse en una tarea compleja, especialmente cuando hay múltiples restricciones que deben respetarse: disponibilidad de docentes, número de salones, cursos obligatorios, entre otros. Este sistema ha sido creado para automatizar ese proceso, aprovechando la potencia de la inteligencia artificial, concretamente mediante un **algoritmo genético**.

Desde una interfaz amigable, podrás cargar tus datos, ajustar los parámetros del algoritmo y generar un horario completo y optimizado que evite conflictos comunes. Además, podrás visualizar y exportar los resultados de forma clara y profesional.

Este manual te guiará paso a paso, desde la preparación inicial hasta la interpretación de los resultados.

---

## 2. ¿Para quién está pensado este sistema?

Este software fue diseñado pensando en usuarios que, aunque no necesariamente tengan experiencia en programación, están involucrados en la organización académica. Es ideal para:

- Coordinadores de carrera o jefes de departamento.
- Personal administrativo de universidades o institutos.
- Docentes encargados de planificar horarios.
- Estudiantes que deseen explorar la aplicación práctica de la inteligencia artificial.

---

## 3. Requisitos para utilizar el sistema

### 🧰 Software necesario

- **Python 3.10 o superior** (instalado en tu sistema)
- Sistema operativo: **Windows, Linux o macOS**
- Librerías adicionales de Python (una sola instalación):

```bash
pip install matplotlib reportlab psutil
```

---

## 4. Archivos necesarios

Todos los archivos deben colocarse en una carpeta llamada `data/`, la cual debe estar en la raíz del proyecto. A continuación te explicamos cómo deben estar estructurados:

### 📄 `cursos.csv`

Contiene todos los cursos a asignar.

| codigo | nombre            | carrera                | semestre | tipo        | seccion |
| ------ | ----------------- | ---------------------- | -------- | ----------- | ------- |
| 101    | Matemática Básica | Ingeniería en Sistemas | 1        | obligatorio | A       |

- **tipo** debe ser `obligatorio` u `optativo`
- **semestre** debe ser un número entero (1 al 10)

---

### 📄 `docentes.csv`

Lista de docentes disponibles.

| registro | nombre          |
| -------- | --------------- |
| D001     | Lic. Juan Pérez |

---

### 📄 `salones.csv`

Lista de espacios físicos disponibles para clases.

| id  | nombre    |
| --- | --------- |
| 1   | Salón 101 |

---

### 📄 `relaciones.csv`

Define qué docente puede impartir qué curso.

| curso_codigo | docente_id |
| ------------ | ---------- |
| 101          | D001       |

---

## 5. Cómo ejecutar el sistema

### En Windows:

```bash
python main.py
```

### En macOS o Linux:

```bash
python3 main.py
```

---

## 6. Navegando por la interfaz
![image](https://github.com/user-attachments/assets/9dc43099-90bd-43b5-9e07-cfdd7c5dc3f7)

Al ejecutar el sistema, se abrirá una ventana gráfica donde interactuarás con todas las funcionalidades. Está dividida en secciones:

### 🎯 1. Selección de Semestre

Aquí decides si deseas generar horarios para **semestres pares** (2, 4, 6, 8, 10) o **impares** (1, 3, 5, 7, 9). Esto ayuda a filtrar los cursos desde el inicio.

![image](https://github.com/user-attachments/assets/6d54bcf2-a1f0-4087-b9fc-423ac2f31a00)


---

### ⚙ 2. Parámetros del algoritmo

Esta sección te permite configurar cómo se comportará el algoritmo genético.

- **Población inicial**: Cuántas soluciones (horarios) se generan al principio. Valores entre 50-150 son ideales.
- **Número de generaciones**: Cuántas veces se "evolucionarán" los horarios. Cuanto más alto, mejor resultado (pero tarda más).
- **Probabilidad de mutación**: De 0.0 a 1.0. Controla cuántas asignaciones cambian aleatoriamente.
- **Torneo k**: Tamaño del grupo que compite en la selección. Recomendado entre 3-5.
- **Aptitud meta**: Si se alcanza este valor, el algoritmo se detiene antes de completar todas las generaciones.

![image](https://github.com/user-attachments/assets/f544d8c4-642d-49fc-80b7-fdd0ae84d4a8)

---

### 🛠 3. Botones principales

- **Generar horario**: Lanza el algoritmo.
- **Seleccionar cursos/docentes**: Elige manualmente qué cursos y profesores incluir.
- **Asignar manualmente**: Puedes bloquear una clase para que ocurra a una hora/salón específicos.
- **Exportar a HTML / PDF / CSV**: Guarda el resultado con formato.
- **Cursos faltantes**: Muestra qué cursos no pudieron ubicarse.
- **Ver evolución**: Grafica cómo mejora la calidad del horario a lo largo de las generaciones.

![image](https://github.com/user-attachments/assets/70b81cbe-e229-49e4-b65f-22ef5c8e935f)

---

## 7. Interpretando los resultados

### 🗓 Tabla de Horario

Se muestra como una **tabla de doble entrada**:

- **Columnas**: Salones disponibles
- **Filas**: Horas disponibles
- **Contenido de cada celda**: Curso, docente, carrera, semestre y sección asignados a esa hora y salón.

Los colores de fondo ayudan a distinguir entre carreras distintas.

![image](https://github.com/user-attachments/assets/4a169f0e-b52c-4329-952c-271d8ee959c7)

---

### 📊 Reporte visual (parte inferior)

Aquí podrás ver:

- Número total de cursos, docentes, salones y asignaciones.
- Conflictos detectados (docente/salón/semestre).
- Cursos obligatorios que no fueron ubicados.
- Bloques continuos: si hay clases seguidas para facilitar la jornada.
- Porcentaje de cursos obligatorios del mismo semestre ubicados en horarios consecutivos.
- Iteración donde se alcanzó la mejor solución.
- Tiempo de ejecución total.
- Memoria RAM utilizada durante el proceso.

![image](https://github.com/user-attachments/assets/45aa11e0-c821-4a9b-9f1e-843c5e417a49)

---

## 8. Exportaciones disponibles

### 📃 HTML

- Representación visual del horario
- Incluye métricas en una tabla
- Fácil de abrir y compartir

---

### 📄 PDF

- Documento más formal
- Ideal para presentaciones o impresión
- Compatible con cualquier lector PDF

---

### 📊 CSV

- Guarda el historial del algoritmo
- Cada línea representa una generación:
  - Generación
  - Aptitud
  - Número de conflictos

---

### 📈 Gráfico de evolución

- Se abre en una nueva ventana
- Muestra cómo mejora la aptitud con cada generación
- Permite detectar si hubo estancamiento o mejora continua

![image](https://github.com/user-attachments/assets/7d54a441-013e-43b5-b766-1cd9adf6d709)

---

## 9. Consejos para un buen resultado

- Verifica que todos los archivos CSV estén bien formateados y tengan datos coherentes.
- Asegúrate de que cada curso obligatorio tenga al menos un docente asignado en `relaciones.csv`.
- Si ves muchos cursos faltantes, revisa posibles conflictos:
  - Falta de salones
  - Docentes ocupados
  - Cursos sin relaciones
- Puedes modificar la cantidad de generaciones o población para obtener mejores horarios.
- Aumentar la probabilidad de mutación puede ayudar a salir de soluciones estancadas.

---

## 10. Problemas comunes y cómo solucionarlos

| Problema                                    | Posible causa                                        | Solución                                               |
| ------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------ |
| La ventana no abre                          | Python no instalado correctamente                    | Ejecuta `python --version` y reinstala si es necesario |
| Un curso no aparece en el horario           | No tiene docente asignado o hay muchas restricciones | Revisa `relaciones.csv` y bloqueos                     |
| El horario generado tiene muchos conflictos | Pocos datos o mal configurados                       | Aumenta la población o ajusta parámetros               |
| El algoritmo se queda estancado             | Baja variabilidad genética                           | Aumenta la mutación o modifica la población inicial    |
