from Scanner import Scanner
from Token import Token
from platformdirs import user_data_dir
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

history_file = Path(user_data_dir("plox", ensure_exists=True)) / ".plox_history"
promptsession: PromptSession[str] = PromptSession(history=FileHistory(history_file))

class Plox():
    def __init__(self:Plox) -> Plox:
        self.mode:None = None

    def process(self:Plox, line:str) -> None:

        scanner:Scanner = Scanner(line)
        tokens:list[Token] = scanner.scan_tokens()




    def main(self : Plox) -> None:
        while True:
            try:
                line:str = promptsession.prompt("> ")
            except (EOFError, KeyboardInterrupt):
                break

            self.process(line)


def main() -> None:
    plox : Plox = Plox()
    plox.main()

if __name__ == "__main__":
    main()