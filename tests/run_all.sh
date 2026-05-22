#!/usr/bin/env bash
# Corre todos los casos en orden.
#
# Uso:
#   1. python receptor.py        (otra terminal)
#   2. bash tests/run_all.sh

DIR="$(dirname "$0")"

VERDE='\033[0;32m'
ROJO='\033[0;31m'
AMARILLO='\033[1;33m'
AZUL='\033[0;34m'
GRIS='\033[0;37m'
NC='\033[0m'

echo ""
printf "${AZUL}╔══════════════════════════════════════════════╗${NC}\n"
printf "${AZUL}║   SUITE DE TESTS — Webhook de Pagos          ║${NC}\n"
printf "${AZUL}╚══════════════════════════════════════════════╝${NC}\n"
echo ""

printf "Verificando servidor en localhost:5000… "
if ! curl -s --max-time 2 -o /dev/null "http://localhost:5000/health" 2>/dev/null; then
    printf "${ROJO}NO DISPONIBLE${NC}\n\n"
    echo "❌  Ejecuta en otra terminal: python receptor.py"
    exit 1
fi
printf "${VERDE}OK${NC}\n"

printf "Reseteando base de datos… "
RESET=$(curl -s -X POST "http://localhost:5000/admin/reset" 2>/dev/null)
if [ "$RESET" = '{"status":"ok"}' ]; then
    printf "${VERDE}OK${NC}\n"
else
    printf "${AMARILLO}no disponible — continúa con estado actual${NC}\n"
fi

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

caso "c1-pago-exitoso"
correr "$DIR/c1-pago-exitoso/1_cliente_paga.sh"
correr "$DIR/c1-pago-exitoso/2_notificacion.sh"

caso "c2-pago-fallido"
correr "$DIR/c2-pago-fallido/1_cliente_paga.sh"
correr "$DIR/c2-pago-fallido/2_notificacion.sh"

caso "c3-reembolso"
correr "$DIR/c3-reembolso/1_notificacion.sh"

caso "c4-firma-invalida"
correr "$DIR/c4-firma-invalida/1_ataque.sh"

caso "c5-idempotencia"
correr "$DIR/c5-idempotencia/1_primer_envio.sh"
correr "$DIR/c5-idempotencia/2_reintento.sh"

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
