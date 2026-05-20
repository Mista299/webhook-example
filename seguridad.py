import hashlib
import hmac

from config import WEBHOOK_SECRET


def verificar_firma(payload_bytes: bytes, firma_recibida: str) -> bool:
    """
    Recalcula la firma HMAC-SHA256 del cuerpo recibido y la compara
    con la que envió el emisor. Si no coinciden → request rechazado.

    compare_digest evita ataques de timing (no cortocircuita en el
    primer byte diferente).
    """
    firma_esperada = hmac.new(
        key=WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(firma_esperada, firma_recibida)
