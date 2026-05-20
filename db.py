"""
Capa de acceso a datos — SQLite.

Todas las operaciones de BD pasan por aquí. El resto del código no
conoce SQL; solo llama funciones con nombres de negocio.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "tienda.db"

# ─────────────────────────────────────────────────────────────
# Conexión
# ─────────────────────────────────────────────────────────────

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # acceso por nombre de columna
    return conn


# ─────────────────────────────────────────────────────────────
# Inicialización
# ─────────────────────────────────────────────────────────────

def init_db():
    """Crea las tablas y carga los pedidos de ejemplo si no existen."""
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id       TEXT PRIMARY KEY,
                producto TEXT NOT NULL,
                total    REAL NOT NULL,
                estado   TEXT NOT NULL DEFAULT 'pendiente'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS eventos_procesados (
                evento_id    TEXT PRIMARY KEY,
                procesado_en TEXT NOT NULL
            )
        """)
        # INSERT OR IGNORE: no sobreescribe si ya existen datos
        conn.executemany(
            "INSERT OR IGNORE INTO pedidos (id, producto, total, estado) VALUES (?,?,?,?)",
            [
                ("ORD-001", "Laptop",      1200.00, "pendiente"),
                ("ORD-002", "Auriculares",   89.99, "pendiente"),
                ("ORD-003", "Teclado",       55.00, "pendiente"),
            ],
        )


def reset_db():
    """Elimina todos los datos y vuelve al estado inicial."""
    with _conn() as conn:
        conn.execute("DELETE FROM pedidos")
        conn.execute("DELETE FROM eventos_procesados")
    init_db()


# ─────────────────────────────────────────────────────────────
# Pedidos
# ─────────────────────────────────────────────────────────────

def get_pedido(pid: str) -> dict | None:
    with _conn() as conn:
        row = conn.execute("SELECT * FROM pedidos WHERE id = ?", (pid,)).fetchone()
        return dict(row) if row else None


def update_estado(pid: str, estado: str):
    with _conn() as conn:
        conn.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (estado, pid))


def listar_pedidos() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM pedidos ORDER BY id").fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Idempotencia
# ─────────────────────────────────────────────────────────────

def evento_ya_procesado(evento_id: str) -> bool:
    with _conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM eventos_procesados WHERE evento_id = ?", (evento_id,)
        ).fetchone()
        return row is not None


def marcar_procesado(evento_id: str):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO eventos_procesados (evento_id, procesado_en) VALUES (?, ?)",
            (evento_id, datetime.now().isoformat(timespec="seconds")),
        )


def listar_eventos() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM eventos_procesados ORDER BY procesado_en"
        ).fetchall()
        return [dict(r) for r in rows]
