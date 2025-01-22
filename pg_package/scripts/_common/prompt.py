import sys
from typing import Any


def prompt_yes_no(question) -> bool:
    """
    prompt [y/n] over question
    """
    valid = {"y": True, "n": False}

    while True:
        sys.stdout.write(f'[INPUT] {question} [y/n]: ')
        choice = input().lower()
        if choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("[INPUT] Please respond with 'y' or 'n'.\n")


def prompt_notice(notice: str) -> None:
    sys.stdout.write(f"[NOTICE] {notice}\n")


def prompt_sql_command(command: str, parameters: Any) -> None:
    sys.stdout.write(f"[SQL-COMMAND] {command} [PARAMS]={parameters}\n")


def prompt_error(err: str) -> None:
    sys.stdout.write(f"[ERROR] {err}\n")
