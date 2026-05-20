"""
Reinicia la base de datos al estado inicial.

Útil para volver a correr los tests .sh desde cero:
    python reset_db.py
    bash tests/run_all.sh
"""

from db import init_db, reset_db

reset_db()

print()
print("✅  Base de datos reiniciada.")
print("   Todos los pedidos → PENDIENTE")
print("   Eventos procesados → vaciado")
print()
print("   Ahora puedes correr de nuevo:")
print("   → python main.py")
print("   → bash tests/run_all.sh")
print()
