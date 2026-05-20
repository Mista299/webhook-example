# Configuración compartida entre receptor y emisor.
# En producción: variables de entorno, nunca texto plano en el código.

WEBHOOK_SECRET = "mi_clave_super_secreta_123"
WEBHOOK_URL    = "http://localhost:5000/webhook/pagos"
PORT           = 5000
