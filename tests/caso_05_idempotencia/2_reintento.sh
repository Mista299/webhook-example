#!/usr/bin/env bash
# Stripe reenvía el mismo evento (mismo ID) porque no recibió
# confirmación a tiempo. El servidor lo detecta en BD y lo ignora.

source "$(dirname "$0")/../_helpers.sh"

titulo "CASO 5 — Paso 2/2: Reintento con el mismo evento"
echo "  Escenario: Stripe reenvía el mismo webhook por error de red."
echo "  El ID 'evt_idem' ya está en la tabla eventos_procesados."
echo "  Resultado esperado: HTTP 200 — 'duplicado, ignorado'"
echo ""

PAYLOAD='{"id":"evt_idem","tipo":"pago.exitoso","datos":{"pedido_id":"ORD-001","monto":1200.0,"cliente":"ana@email.com"}}'
enviar "$PAYLOAD" 200
