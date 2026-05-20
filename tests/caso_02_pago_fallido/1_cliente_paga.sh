#!/usr/bin/env bash
# El cliente intenta pagar los auriculares. La tienda envía el
# cobro a Stripe y el pedido queda en PROCESANDO.

source "$(dirname "$0")/../_helpers.sh"

titulo "CASO 2 — Paso 1/2: Cliente intenta pagar"
echo "  Pedido  : ORD-002 — Auriculares (\$89.99)"
echo "  Acción  : POST /pedidos/ORD-002/checkout"
echo "  Resultado esperado: estado PENDIENTE → PROCESANDO"
echo ""

HTTP=$(curl -s -o /tmp/_wh_resp.txt -w "%{http_code}" \
    -X POST "http://localhost:5000/pedidos/ORD-002/checkout" \
    -H "Content-Type: application/json")

printf "  ${GRIS}Respuesta :${NC} %s\n" "$(cat /tmp/_wh_resp.txt)"

if [ "$HTTP" = "200" ]; then
    printf "  ${VERDE}HTTP %s ✅  Solicitud enviada — esperando respuesta de Stripe…${NC}\n" "$HTTP"
    exit 0
else
    printf "  ${ROJO}HTTP %s ❌  Error en checkout${NC}\n" "$HTTP"
    exit 1
fi
