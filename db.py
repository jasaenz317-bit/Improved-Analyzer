from pathlib import Path
from typing import Union
import sqlite3
from .transactions import Transaction


def get_connection(db_path: Union[str, Path]) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Union[str, Path]) -> None:
    """Initialize the SQLite database and create the transactions table."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT,
            amount TEXT NOT NULL,
            category TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def insert_transaction(db_path: Union[str, Path], tx: Transaction) -> int:
    """Insert a `Transaction` into the DB. Returns the inserted row id."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (date, description, amount, category) VALUES (?, ?, ?, ?)",
        (tx.date.isoformat(), tx.description, str(tx.amount), tx.category),
    )
    rowid = cur.lastrowid
    conn.commit()
    conn.close()
    return rowid
