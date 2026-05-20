#!/usr/bin/env bash
# El cliente pulsa "Pagar". La tienda notifica a Stripe y
# el pedido queda en PROCESANDO hasta recibir el webhook.

source "$(dirname "$0")/../_helpers.sh"

titulo "CASO 1 — Paso 1/2: Cliente inicia el pago"
echo "  Pedido  : ORD-001 — Laptop (\$1200)"
echo "  Acción  : POST /pedidos/ORD-001/checkout"
echo "  Resultado esperado: estado PENDIENTE → PROCESANDO"
echo ""

HTTP=$(curl -s -o /tmp/_wh_resp.txt -w "%{http_code}" \
    -X POST "http://localhost:5000/pedidos/ORD-001/checkout" \
    -H "Content-Type: application/json")

printf "  ${GRIS}Respuesta :${NC} %s\n" "$(cat /tmp/_wh_resp.txt)"

if [ "$HTTP" = "200" ]; then
    printf "  ${VERDE}HTTP %s ✅  Pago enviado — esperando webhook de Stripe…${NC}\n" "$HTTP"
    exit 0
else
    printf "  ${ROJO}HTTP %s ❌  Error en checkout${NC}\n" "$HTTP"
    exit 1
fi
