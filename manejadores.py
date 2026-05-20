from db import get_pedido, update_estado


def procesar_pago_exitoso(datos: dict):
    pid = datos["pedido_id"]
    if not get_pedido(pid):
        print(f"  ⚠️  Pedido {pid} no existe en la BD")
        return
    update_estado(pid, "pagado")
    print(f"  ✅ {pid} PAGADO — cliente: {datos['cliente']}, monto: ${datos['monto']}")
    print(f"     → Email de confirmación enviado")
    print(f"     → Almacén notificado para preparar envío")


def procesar_pago_fallido(datos: dict):
    pid = datos["pedido_id"]
    if not get_pedido(pid):
        print(f"  ⚠️  Pedido {pid} no existe en la BD")
        return
    update_estado(pid, "fallido")
    razon = datos.get("razon", "desconocida")
    print(f"  ❌ {pid} FALLIDO — razón: {razon}")
    print(f"     → Cliente notificado para reintentar el pago")


def procesar_reembolso(datos: dict):
    pid = datos["pedido_id"]
    if not get_pedido(pid):
        print(f"  ⚠️  Pedido {pid} no existe en la BD")
        return
    update_estado(pid, "reembolsado")
    print(f"  🔄 {pid} REEMBOLSO de ${datos['monto']}")
    print(f"     → Devolución al método de pago original procesada")


MANEJADORES = {
    "pago.exitoso":   procesar_pago_exitoso,
    "pago.fallido":   procesar_pago_fallido,
    "pago.reembolso": procesar_reembolso,
}
