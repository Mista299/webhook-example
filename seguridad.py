import hashlib
import hmac

from config import WEBHOOK_SECRET

_SEP = "─" * 54


def verificar_firma(payload_bytes: bytes, firma_recibida: str) -> bool:
    """
    Recalcula la firma HMAC-SHA256 del cuerpo recibido y la compara
    con la que envió el emisor. Si no coinciden → request rechazado.

    compare_digest evita ataques de timing (no cortocircuita en el
    primer byte diferente).
    """
    print(f"\n  {_SEP}")
    print(f"  🔐  VERIFICACIÓN DE AUTENTICIDAD")
    print(f"  {_SEP}")
    print(f"  Firma recibida en cabecera X-Firma-Webhook:")
    print(f"    {firma_recibida[:32] if firma_recibida else '(vacía)'}")
    print(f"    {firma_recibida[32:] if len(firma_recibida) > 32 else ''}")
    print(f"  {_SEP}")
    print(f"  🔄  RECALCULANDO FIRMA (mismo algoritmo que el emisor)")
    print(f"    Clave secreta  : {WEBHOOK_SECRET}")
    print(f"    Payload ({len(payload_bytes)} bytes): {payload_bytes.decode('utf-8', errors='replace')}")
    print(f"    Algoritmo      : HMAC-SHA256")
    print(f"    Pasos:")
    print(f"      1. Codificar clave secreta → bytes UTF-8")
    print(f"      2. Aplicar HMAC(key=clave, msg=payload, digest=SHA-256)")
    print(f"      3. Convertir digest binario → hexadecimal (64 chars)")

    firma_esperada = hmac.new(
        key=WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()

    print(f"    Firma recalculada:")
    print(f"      {firma_esperada[:32]}")
    print(f"      {firma_esperada[32:]}")
    print(f"  {_SEP}")
    print(f"  🔍  COMPARACIÓN DE FIRMAS (hmac.compare_digest — tiempo constante)")
    print(f"  {_SEP}")
    fr = firma_recibida if firma_recibida else "(vacía)"
    print(f"    Recibida ({len(firma_recibida)} chars):")
    print(f"      {firma_recibida[:32] if firma_recibida else '(vacía)'}")
    print(f"      {firma_recibida[32:64]}")
    print(f"    Esperada (64 chars):")
    print(f"      {firma_esperada[:32]}")
    print(f"      {firma_esperada[32:]}")

    # Comparación carácter a carácter
    if firma_recibida and len(firma_recibida) == len(firma_esperada):
        marcas = "".join("✓" if a == b else "✗" for a, b in zip(firma_recibida, firma_esperada))
        diffs  = marcas.count("✗")
        print(f"    Posición a posición:")
        print(f"      {marcas[:32]}")
        print(f"      {marcas[32:]}")
        if diffs == 0:
            print(f"    → 64/64 posiciones coinciden")
        else:
            print(f"    → {64 - diffs}/64 posiciones coinciden, {diffs} distintas")
    else:
        print(f"    → Longitudes distintas: recibida={len(firma_recibida)}, esperada=64")
        print(f"    → Imposible coincidir")

    resultado = hmac.compare_digest(firma_esperada, firma_recibida)
    if resultado:
        print(f"\n  ┌{'─'*50}┐")
        print(f"  │  ✅  FIRMAS COINCIDEN → request AUTÉNTICO        │")
        print(f"  └{'─'*50}┘")
    else:
        print(f"\n  ┌{'─'*50}┐")
        print(f"  │  ❌  FIRMAS NO COINCIDEN → request RECHAZADO     │")
        print(f"  └{'─'*50}┘")
    print(f"  {_SEP}")

    return resultado
