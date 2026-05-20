#!/usr/bin/env bash
# Corre todos los casos en orden.
#
# Uso:
#   1. python receptor.py        (otra terminal)
#   2. bash tests/run_all.sh

DIR="$(dirname "$0")"

VERDE='\033[0;32m'
ROJO='\033[0;31m'
AZUL='\033[0;34m'
GRIS='\033[0;37m'
NC='\033[0m'

echo ""
printf "${AZUL}╔══════════════════════════════════════════════╗${NC}\n"
printf "${AZUL}║   SUITE DE TESTS — Webhook de Pagos          ║${NC}\n"
printf "${AZUL}╚══════════════════════════════════════════════╝${NC}\n"
echo ""

printf "Verificando servidor en localhost:5000… "
if ! curl -s --max-time 2 -o /dev/null \
     -X POST "http://localhost:5000/webhook/pagos" \
     -H "X-Firma-Webhook: test" \
     -H "Content-Type: application/json" \
     -d '{}' 2>/dev/null; then
    printf "${ROJO}NO DISPONIBLE${NC}\n\n"
    echo "❌  Ejecuta en otra terminal: python receptor.py"
    exit 1
fi
printf "${VERDE}OK${NC}\n"

PASADOS=0
FALLADOS=0

correr() {
    local script="$1"
    printf "\n${GRIS}  ▶ $(basename $script)${NC}\n"
    if bash "$script"; then
        PASADOS=$((PASADOS + 1))
    else
        FALLADOS=$((FALLADOS + 1))
    fi
    sleep 0.4
}

caso() {
    printf "\n${AZUL}── %s ──────────────────────────────────────${NC}\n" "$1"
}

caso "caso_01_pago_exitoso"
correr "$DIR/caso_01_pago_exitoso/1_cliente_paga.sh"
correr "$DIR/caso_01_pago_exitoso/2_notificacion.sh"

caso "caso_02_pago_fallido"
correr "$DIR/caso_02_pago_fallido/1_cliente_paga.sh"
correr "$DIR/caso_02_pago_fallido/2_notificacion.sh"

caso "caso_03_reembolso"
correr "$DIR/caso_03_reembolso/1_notificacion.sh"

caso "caso_04_firma_invalida"
correr "$DIR/caso_04_firma_invalida/1_ataque.sh"

caso "caso_05_idempotencia"
correr "$DIR/caso_05_idempotencia/1_primer_envio.sh"
correr "$DIR/caso_05_idempotencia/2_reintento.sh"

echo ""
printf "${AZUL}══════════════════════════════════════════════${NC}\n"
if [ "$FALLADOS" -eq 0 ]; then
    printf "${VERDE}  ✅  Todos los tests pasaron (%d/%d)${NC}\n" \
        "$PASADOS" "$((PASADOS + FALLADOS))"
else
    printf "${ROJO}  ❌  %d fallados, %d pasados${NC}\n" "$FALLADOS" "$PASADOS"
fi
printf "${AZUL}══════════════════════════════════════════════${NC}\n\n"

[ "$FALLADOS" -eq 0 ] && exit 0 || exit 1
