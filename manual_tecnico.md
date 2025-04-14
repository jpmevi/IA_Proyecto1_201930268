# Manual Técnico del Proyecto: Generador de Horarios con Algoritmo Genético

## 1. Descripción General

Este proyecto consiste en un sistema de generación automática de horarios académicos utilizando un algoritmo genético implementado en Python. Mediante una interfaz gráfica intuitiva creada con Tkinter, el usuario puede cargar datos académicos desde archivos CSV, seleccionar semestres, configurar los parámetros evolutivos, visualizar los horarios generados y exportar resultados en múltiples formatos. El sistema es robusto, extensible y diseñado para adaptarse a nuevas restricciones o condiciones futuras.

## 2. Estructura del Proyecto

```
proyecto/
│
├── main.py                  # Aplicación principal: GUI y lógica de control
├── clases/
│   ├── algoritmo.py         # Clase central del algoritmo genético (bucle evolutivo)
│   ├── cargador.py          # Módulo de carga de archivos CSV
│   ├── cruce.py             # Operador de cruce genético (intercambio entre padres)
│   ├── evaluador.py         # Lógica de evaluación de individuos y restricciones
│   ├── generador.py         # Generador de población inicial con reglas duras
│   ├── modelos.py           # Estructuras base: Curso, Docente, Asignación, Individuo, etc.
│   ├── mutador.py           # Operador de mutación para modificar individuos
│   └── seleccionador.py     # Selección por torneo entre individuos
├── data/                    # Archivos CSV: cursos, docentes, salones, relaciones
└── export/                  # Carpeta opcional para exportaciones HTML, PDF, CSV
```

## 3. Algoritmo Genético

### Descripción Técnica

Se utiliza un algoritmo genético canónico para resolver el problema de asignación de horarios con restricciones. Está diseñado para optimizar bajo penalizaciones y bonificaciones múltiples, con operadores personalizados que respetan la naturaleza del problema (evitando cursos duplicados, conflictos de salón/docente, etc.).

### Flujo del Algoritmo

```
Generar población inicial → Evaluar aptitud → Seleccionar padres → Cruzar → Mutar → Evaluar nueva población → Repetir hasta condición de parada
```

### Representación de Individuo

Cada individuo representa un horario completo, compuesto por un conjunto de Asignaciones (curso + docente + salón + hora).

### Evaluación (aptitud)

La clase EvaluadorAptitud mide la calidad de un individuo considerando:

- Penalización por:

  - Conflictos de docente (mismo horario)
  - Conflictos de salón (mismo horario)
  - Obligatorios del mismo semestre en paralelo
  - Cursos obligatorios faltantes

- Bonificación por:
  - Cursos obligatorios ubicados en bloques horarios continuos (delta 50 min)
  - Cursos del mismo semestre ubicados en bloques consecutivos (cálculo por conjunto)

La función de aptitud total:

```
aptitud = -conflictos + continuidad + bloques_seguidos
```

### Selección: Torneo k

Implementado en seleccionador.py. Se escogen aleatoriamente k individuos y se elige el de mayor aptitud para reproducción. Aumenta la presión selectiva.

### Cruce: Intercambio aleatorio de asignaciones

Clase `Cruce`:

- Se seleccionan dos padres.
- Se copian sus asignaciones.
- Se elige un subconjunto aleatorio que se intercambia.
- Se reconstruyen los hijos asegurando validez (no duplicar cursos, ni romper reglas duras).

### Mutación: Reemplazo controlado

Clase `Mutador`:

- Con una probabilidad definida, se selecciona un curso del individuo.
- Se elimina su asignación actual.
- Se intenta reubicar con otra combinación válida de salón/docente/hora.

### Generación Inicial: Aleatoria válida

Clase `GeneradorPoblacion`: genera individuos completamente válidos desde cero respetando:

- Docentes disponibles por curso (según relaciones)
- Horarios no ocupados por salón ni docente
- Reglas duras como cursos obligatorios por semestre y carrera

### Criterios de Parada

1. Se alcanza el número máximo de generaciones.
2. Se alcanza una aptitud igual o superior a la **aptitud meta**.

### Métricas Calculadas por Individuo

- `aptitud_final`
- `conflictos_docente`, `conflictos_salon`, `conflictos_semestre`
- `cursos_faltantes`
- `continuidad_bloques`
- `bloques_seguidos`
- `cursos_consecutivos_unicos`: conjunto de cursos únicos en bloques consecutivos

### Reporte Final

- Iteración donde se obtuvo la mejor solución (`gen_optima`)
- Tiempo total de ejecución (`tiempo_ejec`)
- Porcentaje de cursos obligatorios del mismo semestre ubicados en bloques consecutivos (`porc_consecutivos`)
- Memoria RAM consumida (`psutil.Process(...).memory_info().rss` en bytes)

## 4. Requisitos del Sistema

### Requisitos de Software

- Python ≥ 3.10
- Librerías externas:
  - `matplotlib`
  - `reportlab`
  - `psutil`

Instalación:

```bash
pip install matplotlib reportlab psutil
```

## 5. Ejecución del Proyecto

### Linux/macOS:

```bash
python3 main.py
```

### Windows:

```bash
python main.py
```

## 6. Archivos CSV Requeridos

Todos deben estar en la carpeta `data/`:

- `cursos.csv` → `codigo,nombre,carrera,semestre,tipo,seccion`
- `docentes.csv` → `registro,nombre`
- `salones.csv` → `id,nombre`
- `relaciones.csv` → `curso_codigo,docente_id`

## 7. Interfaz Gráfica

El sistema cuenta con una interfaz amigable en `Tkinter` que permite:

- Selección de semestre (par/impar)
- Selección manual de cursos y docentes activos
- Carga y visualización del horario generado
- Reporte visual de métricas con colores distintivos
- Exportación a HTML, PDF, CSV
- Visualización de la evolución de la aptitud por generación (gráfica matplotlib)

## 8. Reportes y Exportaciones

- **HTML:** Representación del horario con estilo y métricas básicas.
- **PDF:** Exportación formal con ReportLab.
- **CSV:** Evolución generacional (`generacion,aptitud_mejor,conflictos`)
- **Gráfica:** Evolución de aptitud (línea por generación)

## 9. Conclusión

Este sistema implementa un enfoque evolutivo robusto y personalizable para resolver un problema NP-difícil como lo es la **generación automática de horarios académicos**. Puede extenderse fácilmente para incluir más restricciones, validaciones o características (como asignaciones múltiples por curso, penalización por horarios extremos, etc.).

## 10. Créditos

- Autor: Juan Pablo Meza Vielman
- Curso: Inteligencia Artificial - Proyecto 1
- Universidad de San Carlos de Guatemala
- Año: 2025
