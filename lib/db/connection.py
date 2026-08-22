import sqlite3
from typing import Optional, Tuple
import database

def get_connection() -> Tuple[Optional[sqlite3.Connection], bool]:
    """
    Returns (connection, is_local_connection).
    This function utilizes the global get_db from the existing database.py module
    to fetch an active connection or initialize it.
    If is_local_connection is True, the caller is responsible for closing it.
    """
    db_inst = database.get_db()
    if db_inst and hasattr(db_inst, "conn") and db_inst.conn is not None:
        return db_inst.conn, False
    return None, False
