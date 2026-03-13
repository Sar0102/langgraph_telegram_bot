

import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

from src.infrastructure.config.settings import Settings


def build_checkpointer(settings: Settings) -> SqliteSaver:
    connection = sqlite3.connect(settings.short_term_memory_path, check_same_thread=False)
    return SqliteSaver(connection)
