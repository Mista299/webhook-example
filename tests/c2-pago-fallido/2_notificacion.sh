#!/usr/bin/env bash
# Stripe intenta cobrar pero el banco rechaza la tarjeta.
# Stripe notifica el fallo a tu servidor con un webhook firmado.

source "$(dirname "$0")/../_helpers.sh"

titulo "CASO 2 — Paso 2/2: Stripe notifica pago fallido"
echo "  Evento  : pago.fallido para ORD-002"
echo "  Razón   : Tarjeta bloqueada por el banco"
echo "  Resultado esperado: estado PROCESANDO → FALLIDO"
echo ""

PAYLOAD='{"id":"evt_002","tipo":"pago.fallido","datos":{"pedido_id":"ORD-002","razon":"Tarjeta bloqueada por el banco"}}'
enviar "$PAYLOAD" 200
