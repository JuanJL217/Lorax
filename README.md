# Lorax Interpreter

TP de la materia Lenguajes y Compiladores de FIUBA.

Integrantes:
- 110418: Juan Juarez - jjuarez@fi.uba.ar
- 108981: Lihuen Carranza - lcarranza@fi.uba.ar

---

# Requisitos e Instalación

Para ejecutar Lorax, necesitas tener instalado **Python 3.14.3** (o una versión compatible).

## 1. Instalar dependencias

Instala las dependencias necesarias (`prompt_toolkit` y `platformdirs`):

```bash
pip install prompt_toolkit platformdirs
```

## 2. Ejecutar pruebas unitarias (Opcional)

Para ejecutar la suite de pruebas unitarias, necesitarás instalar `pytest`:

```bash
pip install pytest
python3.14 -m pytest
```

---

# Características Principales

## 1. Clases, Herencia y Polimorfismo

Lorax soporta programación orientada a objetos de primer nivel. Se implementó una arquitectura completa con soporte para:

- métodos de instancia
- inicializadores (`init()`)
- palabra clave `this`
- herencia mediante `super`
- resolución dinámica de métodos en tiempo de ejecución

El intérprete implementa tipado dinámico real, permitiendo aprovechar polimorfismo puro entre jerarquías de clases.

### Prueba de Clases

```bash
python3.14 -m src.main clase.lox
```

### Prueba de Polimorfismo

```bash
python3.14 -m src.main polimorfismo.lox
```

---

## 2. Listas (Arrays Dinámicos)

Lorax soporta colecciones ordenadas, indexables y mutables mediante sintaxis con corchetes `[ ]`.

Internamente, las listas se representan mediante nodos específicos del AST (`ListExpr` e `IndexSetExpr`) y delegan el almacenamiento a las estructuras `list` nativas de Python.

También poseen soporte orientado a objetos mediante métodos integrados (`BoundNativeMethod`), permitiendo operaciones como:

- `.append()`
- `.pop()`
- `.len()`

### Prueba de Listas

```bash
python3.14 -m src.main list.lox
```

---

## 3. Hashes (Diccionarios)

Lorax incorpora estructuras llave-valor con sintaxis estilo JSON utilizando `{}`.

Los hashes se abstraen mediante nodos específicos del AST y utilizan internamente los `dict` nativos de Python para garantizar acceso eficiente en tiempo constante promedio.

Soportan:

- asignación dinámica de claves
- `.has()`
- `.keys()`
- `.len()`

### Prueba de Hashes

```bash
python3.14 -m src.main hash.lox
```

---

## 4. Demostración Completa (Mini RPG)

El archivo `show.lox` combina todas las arquitecturas implementadas anteriormente en un pequeño ejemplo estilo RPG, integrando:

- clases
- herencia
- listas
- hashes
- operadores postfix
- operadores ternarios
- mutabilidad entre scopes

### Prueba Final

```bash
python3.14 -m src.main show.lox
```

---

# Uso Básico

## Ejecutar un archivo `.lox`

```bash
python3.14 -m src.main archivo.lox
```

## Iniciar modo interactivo (REPL)

```bash
python3.14 -m src.main
```

---

# Arquitectura Interna

Lorax implementa manualmente las principales etapas de un intérprete moderno:

- Scanner (Lexer)
- Parser recursivo descendente
- AST Interpreter
- Resolver estático de scopes
- Environment chain
- Runtime dinámico

El objetivo del proyecto es servir como implementación educativa y extensible de un lenguaje interpretado moderno inspirado en Lox.

---

# Benchmark de Performance

Se realizó un benchmark simple comparando el tiempo de ejecución entre Python y Lorax al ejecutar un bucle `while` desde `0` hasta `1_000_000`.

## Resultados

| Lenguaje | Tiempo aproximado |
|---|---|
| Lorax (AST Interpreter) | ~2.54 segundos |
| Python (Bytecode VM en C) | ~0.06 segundos |

La diferencia de rendimiento es esperable, ya que:

- Lorax interpreta manualmente cada nodo del AST en Python
- Python ejecuta bytecode optimizado sobre una máquina virtual escrita en C

## Ejecutar Benchmark

```bash
python3.14 benchmark.py
```
---

# Créditos

Proyecto basado e inspirado en el repositorio de https://github.com/FdelMazo/plox.