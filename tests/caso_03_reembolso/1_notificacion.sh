#!/usr/bin/env bash
# El cliente devuelve el teclado. Stripe procesa el reembolso
# y notifica a tu servidor con un webhook firmado.
# (No hay checkout previo: el reembolso lo inicia el cliente, no la tienda.)

source "$(dirname "$0")/../_helpers.sh"

titulo "CASO 3 — Reembolso de ORD-003"
echo "  Evento  : pago.reembolso para ORD-003 — Teclado"
echo "  Monto   : \$55.00 devueltos al método de pago original"
echo "  Resultado esperado: estado PENDIENTE → REEMBOLSADO"
echo ""

PAYLOAD='{"id":"evt_003","tipo":"pago.reembolso","datos":{"pedido_id":"ORD-003","monto":55.0}}'
enviar "$PAYLOAD" 200
