"""
Simulador del emisor de webhooks (al estilo Stripe/PayPal).

Ejecutar de forma independiente (requiere que receptor.py esté corriendo):
    python emisor.py
"""

import hashlib
import hmac
import json
import time

import requests

from config import WEBHOOK_SECRET, WEBHOOK_URL


_SEP = "─" * 54


def _firmar(payload_bytes: bytes) -> str:
    return hmac.new(
        key=WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()


def enviar_evento(evento: dict) -> int:
    """Firma y envía un evento al receptor. Devuelve el HTTP status code."""
    payload_bytes = json.dumps(evento, separators=(",", ":")).encode("utf-8")
    firma         = _firmar(payload_bytes)
    timestamp     = str(int(time.time()))

    print(f"\n  {_SEP}")
    print(f"  📤  PREPARANDO ENVÍO")
    print(f"  {_SEP}")
    print(f"  Payload (JSON compacto, sin espacios):")
    print(f"    {payload_bytes.decode('utf-8')}")
    print(f"  Tamaño payload : {len(payload_bytes)} bytes")
    print(f"  {_SEP}")
    print(f"  🔑  GENERACIÓN DE FIRMA HMAC-SHA256")
    print(f"    Clave secreta  : {WEBHOOK_SECRET}")
    print(f"    Algoritmo      : HMAC-SHA256")
    print(f"    Pasos:")
    print(f"      1. Codificar clave secreta → bytes UTF-8")
    print(f"      2. Aplicar HMAC(key=clave, msg=payload, digest=SHA-256)")
    print(f"      3. Convertir el digest binario a hexadecimal (64 chars)")
    print(f"    Firma resultante:")
    print(f"      {firma[:32]}")
    print(f"      {firma[32:]}")
    print(f"  {_SEP}")
    print(f"  Cabeceras HTTP que se envían:")
    print(f"    Content-Type    : application/json")
    print(f"    X-Firma-Webhook : {firma[:32]}…")
    print(f"    X-Timestamp     : {timestamp}")
    print(f"  Destino: POST {WEBHOOK_URL}")
    print(f"  {_SEP}")

    headers = {
        "Content-Type":    "application/json",
        "X-Firma-Webhook": firma,
        "X-Timestamp":     timestamp,
    }
    respuesta = requests.post(WEBHOOK_URL, data=payload_bytes, headers=headers)

    print(f"  ⬅️   Respuesta del receptor: HTTP {respuesta.status_code}")
    print(f"       Body: {respuesta.text.strip()}")

    return respuesta.status_code


def simular_secuencia():
    """Reproduce una secuencia realista de eventos de pago."""
    time.sleep(1.5)  # esperar a que Flask termine de arrancar

    print("\n" + "═" * 50)
    print("🏪  SIMULADOR DE TIENDA ONLINE")
    print("    (Stripe/PayPal hace esto de forma automática)")
    print("═" * 50)

    eventos = [
        # 1. Pago exitoso de la laptop
        {
            "id": "evt_abc123",
            "tipo": "pago.exitoso",
            "datos": {"pedido_id": "ORD-001", "monto": 1200.0, "cliente": "maria@email.com"},
        },
        # 2. Pago fallido de los auriculares
        {
            "id": "evt_def456",
            "tipo": "pago.fallido",
            "datos": {"pedido_id": "ORD-002", "razon": "Tarjeta sin fondos suficientes"},
        },
        # 3. Reintento del mismo pago de la laptop (mismo ID).
        #    La idempotencia lo bloqueará: no se cobra dos veces.
        {
            "id": "evt_abc123",
            "tipo": "pago.exitoso",
            "datos": {"pedido_id": "ORD-001", "monto": 1200.0, "cliente": "maria@email.com"},
        },
        # 4. Reembolso del teclado
        {
            "id": "evt_ghi789",
            "tipo": "pago.reembolso",
            "datos": {"pedido_id": "ORD-003", "monto": 55.0},
        },
    ]

    for evento in eventos:
        time.sleep(1.2)
        print(f"\n🔔  Disparando '{evento['tipo']}'…")
        status = enviar_evento(evento)
        print(f"    Receptor respondió: HTTP {status}")

    print("\n" + "═" * 50)
    print("✅  Simulación completada")
    print("═" * 50)


if __name__ == "__main__":
    simular_secuencia()
