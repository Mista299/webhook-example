#!/usr/bin/env bash
# Importar con: source "$(dirname "$0")/_helpers.sh"
# Requiere: curl, openssl

VERDE='\033[0;32m'
ROJO='\033[0;31m'
AMARILLO='\033[1;33m'
AZUL='\033[0;34m'
GRIS='\033[0;37m'
NC='\033[0m'

SECRET="mi_clave_super_secreta_123"
URL="http://localhost:5000/webhook/pagos"

titulo() {
    printf "\n${AZUL}══════════════════════════════════════════════${NC}\n"
    printf "${AZUL} %s${NC}\n" "$1"
    printf "${AZUL}══════════════════════════════════════════════${NC}\n\n"
}

firmar() {
    # HMAC-SHA256 del payload usando la clave secreta compartida
    printf '%s' "$1" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}'
}

enviar() {
    local payload="$1"
    local http_esperado="${2:-200}"
    local firma
    firma=$(firmar "$payload")

    printf "  ${GRIS}Payload :${NC} %s\n" "$payload"
    printf "  ${GRIS}Firma   :${NC} %.24s…\n" "$firma"

    local http_real
    http_real=$(curl -s -o /tmp/_wh_resp.txt -w "%{http_code}" \
        -X POST "$URL" \
        -H "Content-Type: application/json" \
        -H "X-Firma-Webhook: $firma" \
        -H "X-Timestamp: $(date +%s)" \
        -d "$payload")

    printf "  ${GRIS}Respuesta:${NC} %s\n" "$(cat /tmp/_wh_resp.txt)"

    if [ "$http_real" = "$http_esperado" ]; then
        printf "  ${VERDE}HTTP %s ✅  PASÓ${NC}\n" "$http_real"
        return 0
    else
        printf "  ${ROJO}HTTP %s ❌  FALLÓ (esperado: %s)${NC}\n" "$http_real" "$http_esperado"
        return 1
    fi
}
