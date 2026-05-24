# Lorax Interpreter

TP de la materia Lenguajes y Compiladores de FIUBA.

Integrantes:
- 110418: Juan Juarez - jjuarez@fi.uba.ar
- 108981: Lihuen Carranza - lcarranza@fi.uba.ar

---

# Requisitos e Instalación

Para ejecutar Lorax, necesitas tener instalado **Python 3.14.3** (o una versión compatible).

## 1. Instalar dependencias

Instala las dependencias necesarias (`prompt_toolkit` y `platformdirs`). Se no instalarla solo sera un input clásico de la librería estandar de Python:

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

**Decisiones de Diseño Interno:**
Siguiendo la filosofía del autor original de Lox (Robert Nystrom en *Crafting Interpreters*), decidimos separar por completo la representación estática (AST) de la representación en tiempo de ejecución. 
Por este motivo se crearon archivos independientes como `LoraxClass.py` y `LoraxInstance.py`. Mientras que `Parser.py` solo se encarga de crear el nodo estático `ClassDecl`, `Interpreter.py` es el que instancia la clase viva (`LoraxClass`) en memoria, creando su closure y tabla de métodos. Cuando la clase es "llamada" o instanciada como una función (`MiClase()`), el intérprete crea un objeto `LoraxInstance`. Esta separación permite manejar el estado (los "fields" o propiedades) exclusivamente en la instancia, mientras que los comportamientos (métodos) se comparten en la clase delegando limpiamente el acceso mediante descriptores dinámicos y ligando `this` de manera oculta en el *environment*.

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

**Decisiones de Diseño Interno:**
El lenguaje Lox original delineado en el libro no posee ningún soporte nativo para arreglos dinámicos o listas, priorizando un núcleo de lenguaje mínimo. En Lorax decidimos que era una característica indispensable.

A nivel gramatical, se extendió `Parser.py` para reconocer la sintaxis de listas literales `[a, b, c]` generando el nodo `ListExpr`, y los accesos mediante corchetes `lista[i]` (nodos `IndexExpr` e `IndexSetExpr`). En `Interpreter.py`, en lugar de implementar una estructura de memoria manual para las listas desde cero, delegamos el almacenamiento al `list` nativo subyacente de Python para aprovechar sus optimizaciones en C.

También poseen soporte orientado a objetos mediante métodos integrados delegados a clases polimórficas (como `BoundAppend`, `BoundLen`), permitiendo operaciones como:

- `.append(elemento)`: Agrega un nuevo elemento al final de la lista.
- `.pop(indice)`: Elimina y devuelve el elemento en la posición especificada.
- `.len()`: Devuelve la cantidad total de elementos en la lista.

Para lograr esto sin necesidad de crear clases Lox globales en el código fuente, el intérprete intercepta la evaluación de propiedades (`GetExpr`) de estos objetos e inyecta dinámicamente la clase auxiliar correspondiente según el método llamado, lo que permite encadenar funciones escritas en Python como si fueran métodos puros del usuario (polimorfismo simulado).

### Prueba de Listas

```bash
python3.14 -m src.main list.lox
```

---

## 3. Hashes (Diccionarios)

Lorax incorpora estructuras llave-valor con sintaxis estilo JSON utilizando `{}`.

**Decisiones de Diseño Interno:**
De forma idéntica a las listas, los diccionarios o estructuras hash fueron excluidos deliberadamente del diseño base de Lox. Implementarlos en Lorax requirió extender profundamente el lenguaje.

En la etapa de parseo, `Parser.py` fue modificado para permitir literales `{clave: valor}` que se convierten en un nodo `DictExpr`. Durante la evaluación (`Interpreter.py`), las expresiones indexadas que antes solo servían para listas fueron adaptadas polimórficamente para servir también como operaciones `get` y `set` de claves del diccionario. Internamente, son respaldados por el veloz motor de `dict` de Python, garantizando un acceso eficiente.

Soportan:

- asignación dinámica de claves
- `.has(clave)`: Devuelve `true` si la clave existe en el diccionario, o `false` en caso contrario.
- `.keys()`: Devuelve una lista con todas las claves presentes en el diccionario.
- `.len()`: Devuelve la cantidad de pares clave-valor almacenados.

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

Se realizó un benchmark simple comparando el tiempo de ejecución entre Python y Lorax al ejecutar un bucle `while` desde `0` hasta `1.000.000`.

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