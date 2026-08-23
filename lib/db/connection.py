import sqlite3
from typing import Optional, Tuple
import database

def get_connection() -> Tuple[Optional[sqlite3.Connection], bool]:
    """
    Returns (connection, is_local_connection) for the existing shared database
    connection managed by database.py.

    This helper does not create a fallback local connection. If no active shared
    connection is available, a RuntimeError is raised so callers do not proceed
    with a missing connection.

    The returned is_local_connection flag is always False because ownership of
    the shared connection remains with the database module.
    """
    db_inst = database.get_db()
    if db_inst and hasattr(db_inst, "conn") and db_inst.conn is not None:
        return db_inst.conn, False
    raise RuntimeError("No active database connection is available.")
