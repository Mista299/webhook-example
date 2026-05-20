#!/usr/bin/env bash
# Un atacante intenta inyectar un webhook falso sin conocer
# la clave secreta. El servidor debe rechazarlo con HTTP 401.

source "$(dirname "$0")/../_helpers.sh"

titulo "CASO 4 — Ataque con firma falsa"
echo "  Escenario: alguien envía un webhook SIN la clave secreta real."
echo "  Firma   : cadena aleatoria (no es HMAC válido)"
echo "  Resultado esperado: HTTP 401 — request rechazado"
echo ""

PAYLOAD='{"id":"evt_hack","tipo":"pago.exitoso","datos":{"pedido_id":"ORD-001","monto":9999.0,"cliente":"hacker@mal.com"}}'
FIRMA_FALSA="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

printf "  ${GRIS}Payload :${NC} %s\n" "$PAYLOAD"
printf "  ${GRIS}Firma   :${NC} %.24s… (FALSA)\n" "$FIRMA_FALSA"

HTTP=$(curl -s -o /tmp/_wh_resp.txt -w "%{http_code}" \
    -X POST "$URL" \
    -H "Content-Type: application/json" \
    -H "X-Firma-Webhook: $FIRMA_FALSA" \
    -H "X-Timestamp: $(date +%s)" \
    -d "$PAYLOAD")

printf "  ${GRIS}Respuesta:${NC} %s\n" "$(cat /tmp/_wh_resp.txt)"

if [ "$HTTP" = "401" ]; then
    printf "  ${VERDE}HTTP %s ✅  Ataque bloqueado correctamente${NC}\n" "$HTTP"
    exit 0
else
    printf "  ${ROJO}HTTP %s ❌  FALLÓ (esperado: 401)${NC}\n" "$HTTP"
    exit 1
fi
