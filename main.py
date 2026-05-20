"""
Punto de entrada — arranca servidor y simulador juntos.

    python main.py          ← servidor + simulación automática
    python receptor.py      ← solo el servidor (para tests .sh)
    python emisor.py        ← solo el simulador
    python ver_db.py        ← ver el estado de la base de datos
    python reset_db.py      ← reiniciar la base de datos
    bash tests/run_all.sh   ← suite de tests con curl
"""

import threading

from config import PORT
from db import init_db
from emisor import simular_secuencia
from receptor import app

if __name__ == "__main__":
    init_db()

    print("╔══════════════════════════════════════════════════╗")
    print("║        WEBHOOK RECEIVER — Tienda Online          ║")
    print(f"║  Escuchando en : http://localhost:{PORT}             ║")
    print("║  Endpoint      : POST /webhook/pagos             ║")
    print("║  Base de datos : tienda.db                       ║")
    print("╚══════════════════════════════════════════════════╝")

    hilo = threading.Thread(target=simular_secuencia, daemon=True)
    hilo.start()

    app.run(port=PORT, debug=False)
