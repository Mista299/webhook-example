# 🪝 Webhook de Pagos — Ejemplo Práctico

Simulación de una tienda online que recibe notificaciones de pago al estilo **Stripe**.

---

## ⚙️ Cómo funciona este proyecto

```
                        TIENDA (tú)
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
    receptor.py        emisor.py           tienda.db
    (Flask server)   (simula Stripe)       (SQLite)
          │                 │
          │   POST /webhook/pagos
          │◄────────────────┤
          │   + firma HMAC  │
          │                 │
          ▼                 │
    verifica firma          │
    verifica idempotencia   │
    actualiza BD            │
    HTTP 200 ──────────────►│
```

### Flujo de un pago exitoso (paso a paso)

```
1. Cliente pulsa "Pagar"
        │
        ▼
2. POST /pedidos/ORD-001/checkout      ← receptor.py
   Estado: PENDIENTE → PROCESANDO
        │
        ▼
3. Stripe procesa el cobro…
        │
        ▼
4. POST /webhook/pagos                 ← receptor.py
   Header: X-Firma-Webhook: <hmac>
   Body:   {"tipo": "pago.exitoso", ...}
        │
        ├─ verifica firma HMAC-SHA256
        ├─ comprueba idempotencia en BD
        ├─ actualiza pedido → PAGADO
        └─ responde HTTP 200
```

---

## 🔐 La firma HMAC-SHA256

Emisor y receptor comparten una **clave secreta**. Antes de enviar el webhook, el emisor firma el body:

```
firma = HMAC-SHA256(clave_secreta, body_json)
```

El receptor recalcula la firma con el mismo body y clave. Si no coinciden → `HTTP 401`.

```python
# seguridad.py
firma_esperada = hmac.new(
    key=WEBHOOK_SECRET.encode(),
    msg=payload_bytes,          # bytes exactos del body recibido
    digestmod=hashlib.sha256,
).hexdigest()

return hmac.compare_digest(firma_esperada, firma_recibida)
```

> `compare_digest` evita ataques de timing: siempre tarda lo mismo sin importar cuántos caracteres coincidan.

---

## ♻️ Idempotencia

Si Stripe no recibe el `HTTP 200` a tiempo, **reintenta** el mismo webhook. Sin idempotencia, un pago podría procesarse dos veces.

Cada evento procesado se guarda en `eventos_procesados`. Si llega un evento con el mismo ID → se ignora.

```python
# receptor.py
if evento_ya_procesado(evento_id):
    return jsonify({"status": "duplicado, ignorado"}), 200
```

---

## 📁 Estructura del proyecto

```
exposicion-webhooks/
│
├── config.py          ← clave secreta, URL, puerto
├── seguridad.py       ← verificación HMAC-SHA256
├── manejadores.py     ← lógica por tipo de evento (exitoso, fallido, reembolso)
├── db.py              ← interacción con SQLite
├── receptor.py        ← servidor Flask (endpoints)
├── emisor.py          ← simulador de Stripe
│
├── main.py            ← arranca servidor + simulación automática
├── ver_db.py          ← muestra el estado de la BD
├── reset_db.py        ← reinicia la BD al estado inicial
│
├── tienda.db          ← base de datos SQLite (se crea al ejecutar)
│
└── tests/
    ├── _helpers.sh                        ← firma HMAC y curl compartidos
    ├── run_all.sh                         ← corre todos los casos
    ├── caso_01_pago_exitoso/
    │   ├── 1_cliente_paga.sh              ← checkout → PROCESANDO
    │   └── 2_notificacion.sh             ← webhook  → PAGADO
    ├── caso_02_pago_fallido/
    │   ├── 1_cliente_paga.sh              ← checkout → PROCESANDO
    │   └── 2_notificacion.sh             ← webhook  → FALLIDO
    ├── caso_03_reembolso/
    │   └── 1_notificacion.sh             ← webhook  → REEMBOLSADO
    ├── caso_04_firma_invalida/
    │   └── 1_ataque.sh                   ← firma falsa → HTTP 401
    └── caso_05_idempotencia/
        ├── 1_primer_envio.sh             ← procesado normalmente
        └── 2_reintento.sh               ← mismo ID → ignorado
```

---

## 🚀 Comandos

### Instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Opción A — Todo automático (servidor + simulación)

```bash
python main.py
```

### Opción B — Manual con tests de shell

**Terminal 1 — servidor:**
```bash
python receptor.py
```

**Terminal 2 — tests:**
```bash
# Resetear BD antes de cada sesión de pruebas
python reset_db.py

# Correr todos los casos
bash tests/run_all.sh

# O caso por caso
bash tests/caso_01_pago_exitoso/1_cliente_paga.sh
bash tests/caso_01_pago_exitoso/2_notificacion.sh

bash tests/caso_02_pago_fallido/1_cliente_paga.sh
bash tests/caso_02_pago_fallido/2_notificacion.sh

bash tests/caso_03_reembolso/1_notificacion.sh
bash tests/caso_04_firma_invalida/1_ataque.sh
bash tests/caso_05_idempotencia/1_primer_envio.sh
bash tests/caso_05_idempotencia/2_reintento.sh
```

### Ver y verificar la base de datos

```bash
# Script de Python
python ver_db.py

# O directamente en sqlite3 (ejecutar desde la carpeta del proyecto)
sqlite3 tienda.db
```

```sql
.mode column
.headers on

SELECT * FROM pedidos;               -- estado de los pedidos
SELECT * FROM eventos_procesados;    -- eventos ya procesados (idempotencia)

.quit
```

### Reiniciar la BD

```bash
python reset_db.py    -- vuelve todos los pedidos a PENDIENTE
```

---

## 🗄️ Tablas SQLite

```sql
CREATE TABLE pedidos (
    id       TEXT PRIMARY KEY,   -- ORD-001, ORD-002, ORD-003
    producto TEXT NOT NULL,
    total    REAL NOT NULL,
    estado   TEXT NOT NULL       -- pendiente | procesando | pagado | fallido | reembolsado
);

CREATE TABLE eventos_procesados (
    evento_id    TEXT PRIMARY KEY,   -- ID único del evento (idempotencia)
    procesado_en TEXT NOT NULL       -- timestamp
);
```

---

## 📝 Conceptos clave

| Concepto | ¿Qué resuelve? | Archivo |
|----------|----------------|---------|
| **HMAC-SHA256** | Verificar que el webhook viene de Stripe y no de un atacante | `seguridad.py` |
| **compare_digest** | Evitar ataques de timing en la comparación de firmas | `seguridad.py` |
| **Idempotencia** | Evitar procesar el mismo pago dos veces si Stripe reintenta | `db.py` |
| **HTTP 200 rápido** | Indicarle a Stripe que el evento fue recibido para que no reintente | `receptor.py` |
| **SQLite** | Persistir los estados entre reinicios del servidor | `db.py` |
# ejemplo-webhook
