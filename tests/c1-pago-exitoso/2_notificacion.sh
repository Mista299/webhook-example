#!/usr/bin/env bash
# Stripe procesó el cobro y avisa a tu servidor con un webhook firmado.
# El servidor verifica la firma, actualiza la BD y responde HTTP 200.

source "$(dirname "$0")/../_helpers.sh"

titulo "CASO 1 — Paso 2/2: Stripe notifica pago exitoso"
echo "  Evento  : pago.exitoso para ORD-001"
echo "  Acción  : POST /webhook/pagos  (firmado con HMAC-SHA256)"
echo "  Resultado esperado: estado PROCESANDO → PAGADO"
echo ""

PAYLOAD='{"id":"evt_001","tipo":"pago.exitoso","datos":{"pedido_id":"ORD-001","monto":1200.0,"cliente":"carlos@email.com"}}'
enviar "$PAYLOAD" 200
