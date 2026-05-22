"""
Servidor Flask — receptor de webhooks.

Ejecutar solo (para usar con los tests .sh):
    python receptor.py
"""

import json
import time
from datetime import datetime

from flask import Flask, jsonify, request

from config import PORT
from db import (
    evento_ya_procesado,
    get_pedido,
    init_db,
    listar_pedidos,
    marcar_procesado,
    update_estado,
)
from manejadores import MANEJADORES
from seguridad import verificar_firma

app = Flask(__name__)
SEP = "─" * 50

ICONOS = {"pendiente": "⏳", "procesando": "⚙️ ", "pagado": "✅", "fallido": "❌", "reembolsado": "🔄"}


# ─────────────────────────────────────────────────────────────
# PASO 1: el cliente inicia el pago en la tienda
# ─────────────────────────────────────────────────────────────

@app.route("/pedidos/<pid>/checkout", methods=["POST"])
def checkout(pid):
    """
    Simula que el cliente pulsó 'Pagar'.
    La tienda envía la solicitud de cobro a Stripe y queda en
    estado 'procesando' hasta recibir la confirmación por webhook.
    """
    pedido = get_pedido(pid)
    if not pedido:
        return jsonify({"error": f"Pedido {pid} no encontrado"}), 404
    if pedido["estado"] != "pendiente":
        return jsonify({"error": f"El pedido ya está en estado: {pedido['estado']}"}), 400

    # ID ficticio que Stripe devolvería al crear el PaymentIntent
    payment_id = f"pay_{pid.lower().replace('-', '_')}_{int(time.time())}"
    update_estado(pid, "procesando")

    print(f"\n{SEP}")
    print(f"🛒  Checkout iniciado — {datetime.now().strftime('%H:%M:%S')}")
    print(f"  Pedido   : {pid} — {pedido['producto']} (${pedido['total']})")
    print(f"  Payment  : {payment_id}")
    print(f"  Estado   : PENDIENTE → PROCESANDO")
    print(f"  → Solicitud enviada a Stripe. Esperando webhook de confirmación…")

    return jsonify({
        "pedido_id":  pid,
        "payment_id": payment_id,
        "estado":     "procesando",
        "mensaje":    "Pago enviado a Stripe. Tu servidor recibirá un webhook cuando se confirme.",
    }), 200


# ─────────────────────────────────────────────────────────────
# PASO 2: Stripe confirma el resultado por webhook
# ─────────────────────────────────────────────────────────────

@app.route("/webhook/pagos", methods=["POST"])
def recibir_webhook():
    payload_bytes  = request.get_data()
    firma_recibida = request.headers.get("X-Firma-Webhook", "")
    timestamp      = request.headers.get("X-Timestamp", "N/A")
    ip_origen      = request.remote_addr

    print(f"\n{SEP}")
    print(f"📨  WEBHOOK RECIBIDO — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{SEP}")
    print(f"  IP origen       : {ip_origen}")
    print(f"  Content-Type    : {request.headers.get('Content-Type', 'N/A')}")
    print(f"  X-Timestamp     : {timestamp}")
    print(f"  X-Firma-Webhook : {firma_recibida[:32] if firma_recibida else '(ausente)'}…")
    print(f"  Payload crudo ({len(payload_bytes)} bytes):")
    print(f"    {payload_bytes.decode('utf-8', errors='replace')}")

    # 1. Autenticidad: rechazar si la firma HMAC no cuadra
    if not verificar_firma(payload_bytes, firma_recibida):
        print(f"  🚫  Solicitud rechazada — respuesta: 401 Unauthorized")
        return jsonify({"error": "Firma inválida"}), 401

    print(f"  ✅  Autenticidad confirmada — procesando evento")

    evento    = json.loads(payload_bytes)
    evento_id = evento.get("id")
    tipo      = evento.get("tipo")
    datos     = evento.get("datos", {})

    print(f"\n{SEP}")
    print(f"  📋  EVENTO DECODIFICADO")
    print(f"{SEP}")
    print(f"  ID    : {evento_id}")
    print(f"  Tipo  : {tipo}")
    print(f"  Datos : {json.dumps(datos, ensure_ascii=False)}")

    # 2. Idempotencia: ignorar eventos ya procesados
    print(f"\n{SEP}")
    print(f"  ♻️   VERIFICACIÓN DE IDEMPOTENCIA")
    print(f"{SEP}")
    print(f"  Consultando BD por evento_id='{evento_id}'…")
    if evento_ya_procesado(evento_id):
        print(f"  ⚠️   Encontrado en BD — evento ya procesado anteriormente")
        print(f"  Acción: ignorar (no re-procesar) → respuesta: 200 duplicado")
        return jsonify({"status": "duplicado, ignorado"}), 200
    print(f"  ✅  No encontrado en BD — evento nuevo, se procesará")

    # 3. Despachar al manejador correcto
    print(f"\n{SEP}")
    print(f"  ⚙️   DESPACHANDO MANEJADOR")
    print(f"{SEP}")
    manejador = MANEJADORES.get(tipo)
    if not manejador:
        print(f"  ❓  Sin manejador registrado para tipo '{tipo}'")
        return jsonify({"status": "evento no reconocido"}), 200

    print(f"  Manejador : {manejador.__name__}")
    manejador(datos)

    print(f"\n  Registrando evento_id='{evento_id}' en BD (idempotencia futura)…")
    marcar_procesado(evento_id)
    print(f"  ✅  Registrado")

    _mostrar_pedidos()

    # Responder 200 rápido es CRÍTICO: el emisor deja de reintentar.
    return jsonify({"status": "procesado", "evento_id": evento_id}), 200


def _mostrar_pedidos():
    print(f"\n  📦 Estado actual (desde BD):")
    for p in listar_pedidos():
        icono = ICONOS.get(p["estado"], "?")
        print(f"     {icono}  {p['id']}: {p['producto']:<15} → {p['estado'].upper()}")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/admin/reset", methods=["POST"])
def admin_reset():
    from db import reset_db
    reset_db()
    print(f"\n{SEP}")
    print(f"🔄  BASE DE DATOS RESETEADA — estado inicial restaurado")
    print(f"{SEP}")
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    init_db()
    print("╔══════════════════════════════════════════════════╗")
    print("║        RECEPTOR DE WEBHOOKS — Tienda Online      ║")
    print(f"║  Escuchando en : http://localhost:{PORT}             ║")
    print("║  Endpoint      : POST /webhook/pagos             ║")
    print("║  Base de datos : tienda.db                       ║")
    print("╚══════════════════════════════════════════════════╝")
    app.run(port=PORT, debug=False)
