import argparse
import traceback
from dataclasses import dataclass
import os

from .Scanner import Scanner
from .Parser import Parser
from .Resolver import Resolver
from .Interpreter import Interpreter
from .Token import TokenType

# Si no se descarga eso, no explota, solo usa el input común
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from platformdirs import user_cache_dir
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

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

    def _is_incomplete(self, source: str) -> bool:
        try:
            scanner = Scanner(source)
            tokens = scanner.scan()
            
            open_pairs = 0
            for t in tokens:
                if t.token_type in (TokenType.LEFT_BRACE, TokenType.LEFT_PAREN, TokenType.LEFT_BRACKET):
                    open_pairs += 1
                elif t.token_type in (TokenType.RIGHT_BRACE, TokenType.RIGHT_PAREN, TokenType.RIGHT_BRACKET):
                    open_pairs -= 1
            return open_pairs > 0
        except Exception as e:
            # Si el Scanner detecta un string o comentario sin cerrar, seguimos esperando
            return "Unterminated" in str(e)

    def _better_input(self):
        cache_dir = user_cache_dir("lorax")
        os.makedirs(cache_dir, exist_ok=True)
        session = PromptSession(history=FileHistory(os.path.join(cache_dir, "history.txt")))

        buffer = []
        while True:
            try:
                prompt_char = "> " if not buffer else ". "
                line = session.prompt(prompt_char)
                
                if not line.strip() and not buffer: 
                    continue
                
                buffer.append(line)
                source = "\n".join(buffer)
                
                if self._is_incomplete(source):
                    continue
                
                self.run(source)
                buffer = []
            except (EOFError, KeyboardInterrupt):
                # Si estamos a mitad de un bloque, Ctrl+C lo cancela limpiando el buffer
                if buffer:
                    buffer = []
                    print()
                    continue
                else:
                    print("\nSaliendo...")
                    break

    def _simple_input(self):
        buffer = []
        while True:
            try:
                prompt_char = "> " if not buffer else ". "
                line = input(prompt_char)
                
                if not line.strip() and not buffer: 
                    continue
                
                buffer.append(line)
                source = "\n".join(buffer)
                
                if self._is_incomplete(source):
                    continue
                
                self.run(source)
                buffer = []
            except (EOFError, KeyboardInterrupt):
                if buffer:
                    buffer = []
                    print()
                    continue
                else:
                    print("\nSaliendo...")
                    break

    def run_repl(self):
        print("Lorax REPL - v1.0 (Basado en Lox)")
        if PROMPT_TOOLKIT_AVAILABLE:
            self._better_input()
        else:
            self._simple_input()

    def run_file(self, path: str):
        try:
            with open(path, 'r') as f:
                if self.config.line_by_line:
                    for i, line in enumerate(f, 1):
                        if line.strip():
                            if self.config.mode:
                                print(f"--- Línea {i}: {line.strip()} ---")
                            self.run(line)
                else:
                    self.run(f.read())
        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo '{path}'")

    def run(self, source: str):
        try:
            scanner = Scanner(source)
            tokens = scanner.scan()
            if self.config.mode == "scanning":
                for t in tokens: 
                    print(f"line {t.line} | {t}")
                return

            parser = Parser(tokens)
            statements = parser.parse()
            if not statements: return
            if self.config.mode == "parsing":
                for s in statements: 
                    print(s)
                return

            resolver = Resolver(self.interpreter)
            for s in statements:
                resolver.resolve(s)

            if self.config.mode == "resolve":
                depths = {str(k): v for k, v in self.interpreter.local_scope_depths.items()}
                print(f"Interpreter Locals (Depths): {depths}")
                return

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