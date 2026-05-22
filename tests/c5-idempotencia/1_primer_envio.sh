#!/usr/bin/env bash
# Primer envío del evento. Se procesa normalmente.

source "$(dirname "$0")/../_helpers.sh"

titulo "CASO 5 — Paso 1/2: Primer envío del evento"
echo "  Escenario: Stripe envía el webhook por primera vez."
echo "  Resultado esperado: HTTP 200 — evento procesado"
echo ""

PAYLOAD='{"id":"evt_idem","tipo":"pago.exitoso","datos":{"pedido_id":"ORD-001","monto":1200.0,"cliente":"ana@email.com"}}'
enviar "$PAYLOAD" 200
