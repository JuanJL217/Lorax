import argparse
import traceback
from dataclasses import dataclass

# Tus archivos
from .Scanner import Scanner
from .Parser import Parser
from .Resolver import Resolver
from .Interpreter import Interpreter

@dataclass
class Config:
    mode: str | None = None
    file: str | None = None
    debug: bool = False
    line_by_line: bool = False

class Plox:
    def __init__(self, config: Config):
        self.config = config
        self.interpreter = Interpreter()

    def run_repl(self):
        print("Lorax REPL - v1.0 (Basado en Lox)")
        while True:
            try:
                line = input("> ")
                if not line.strip(): continue
                self.run(line)
            except (EOFError, KeyboardInterrupt):
                print("\nSaliendo...")
                break

    def run_file(self, path: str):
        try:
            with open(path, 'r') as f:
                if self.config.line_by_line:
                    # Lee el archivo línea por línea
                    for i, line in enumerate(f, 1):
                        if line.strip():
                            if self.config.mode:
                                print(f"--- Línea {i}: {line.strip()} ---")
                            self.run(line)
                else:
                    # Lee todo el archivo de una
                    self.run(f.read())
        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo '{path}'")

    def run(self, source: str):
        try:
            # 1. Scanning
            scanner = Scanner(source)
            tokens = scanner.scan()
            if self.config.mode == "scanning":
                for t in tokens: 
                    print(f"line {t.line} | {t}")
                return

            # 2. Parsing
            parser = Parser(tokens)
            statements = parser.parse()
            if not statements: return
            if self.config.mode == "parsing":
                for s in statements: 
                    print(s)
                return

            # 3. Resolving
            resolver = Resolver(self.interpreter)
            for s in statements:
                resolver.resolve(s)

            if self.config.mode == "resolve":
                # Convertimos las llaves a string para que el print sea legible
                depths = {str(k): v for k, v in self.interpreter.local_scope_depths.items()}
                print(f"Interpreter Locals (Depths): {depths}")
                return

            # 4. Interpreting
            self.interpreter.interpret(statements)

        except Exception as e:
            if self.config.debug:
                traceback.print_exc()
            else:
                print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(prog="plox")
    parser.add_argument("--scanning", action="store_true")
    parser.add_argument("--parsing", action="store_true")
    parser.add_argument("--resolve", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--line-by-line", action="store_true", help="Ejecuta el archivo línea por línea")
    parser.add_argument("file", nargs="?")
    
    args = parser.parse_args()
    
    mode = None
    if args.scanning: mode = "scanning"
    elif args.parsing: mode = "parsing"
    elif args.resolve: mode = "resolve"
    
    config = Config(mode=mode, file=args.file, debug=args.debug, line_by_line=args.line_by_line)
    app = Plox(config)
    
    if config.file:
        app.run_file(config.file)
    else:
        app.run_repl()

if __name__ == "__main__":
    main()