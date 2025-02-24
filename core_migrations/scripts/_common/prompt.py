import sys
from typing import Any
import traceback
from datetime import\
    datetime,\
    timezone
import core_migrations.backend.cpp.backend_wrapper as bw


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
    bw.prompt_notice(notice)


def prompt_error(err: str) -> None:
    bw.prompt_error(err, str(traceback.format_exc()))


def log_notice(diag):
    now = datetime.now(timezone.utc)
    sys.stdout.write(f"[SERVER - {now.isoformat()}] {diag.severity} - {diag.message_primary}\n")
