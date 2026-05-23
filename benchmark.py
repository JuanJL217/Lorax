import time
from src.main import Plox, Config

lorax_code = """
var i = 0;
while (i < 1000000) {
    i = i + 1;
}
"""

python_code = """
i = 0
while i < 1000000:
    i += 1
"""

def benchmark_lorax():
    config = Config(mode=None, file=None, debug=False, line_by_line=False)
    app = Plox(config)
    
    start = time.perf_counter()
    app.run(lorax_code)
    end = time.perf_counter()
    
    return end - start

def benchmark_python():
    start = time.perf_counter()
    exec(python_code)
    end = time.perf_counter()
    return end - start

if __name__ == "__main__":
    print("Iniciando benchmark de iteraciones (0 a 10000)...\n")
    
    lorax_time = benchmark_lorax()
    print(f"Tiempo de Lorax (AST Interpreter) : {lorax_time:.5f} segundos")
    
    python_time = benchmark_python()
    print(f"Tiempo de Python (Bytecode C)     : {python_time:.5f} segundos")

