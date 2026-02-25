# apimodbus

Modbus TCP server with a FastAPI REST wrapper, fully containerized with Docker.

## Architecture

Two microservices communicate over a Docker bridge network (`energio_net`):

| Service | Image | Port | Description |
|---|---|---|---|
| `modbus-server` | pymodbus | 502 | Modbus TCP server |
| `api` | FastAPI + uvicorn | 8000 | REST API (Modbus client) |

```
Client (HTTP)
    │
    ▼
FastAPI :8000  ──(Modbus TCP)──►  pymodbus server :502
```

## Requirements

- Docker
- Docker Compose

## Quick Start

```bash
# Build and start both services
docker compose up --build

# Run in background
docker compose up --build -d

# Stop
docker compose down
```

## API Endpoints

### `GET /health`

Check API and Modbus server connectivity.

```bash
curl http://localhost:8000/health
```

```json
{
  "api": "ok",
  "modbus_target": "modbus-server:502",
  "modbus_connect": true
}
```

---

### `GET /read`

Read one or more holding registers (FC03).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `address` | int ≥ 0 | yes | 0-based start address (address 0 = Modbus 40001) |
| `count` | int 1–125 | no (default 1) | Number of registers to read |

```bash
curl "http://localhost:8000/read?address=0&count=3"
```

```json
{
  "address": 0,
  "count": 3,
  "unit": 1,
  "data": [100, 200, 300]
}
```

---

### `POST /write`

Write a single holding register (FC06).

```bash
curl -X POST http://localhost:8000/write \
  -H "Content-Type: application/json" \
  -d '{"address": 0, "value": 42}'
```

```json
{
  "unit": 1,
  "address": 0,
  "value": 42,
  "status": "ok"
}
```

---

### `POST /write-multiple`

Write multiple consecutive holding registers (FC16).

| Field | Type | Description |
|---|---|---|
| `address` | int ≥ 0 | 0-based start address |
| `values` | list of int (1–123 items, each 0–65535) | Values to write consecutively |

```bash
curl -X POST http://localhost:8000/write-multiple \
  -H "Content-Type: application/json" \
  -d '{"address": 0, "values": [100, 200, 300]}'
```

```json
{
  "unit": 1,
  "address": 0,
  "count": 3,
  "values": [100, 200, 300],
  "status": "ok"
}
```

## Interactive API Docs

FastAPI provides auto-generated docs at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

### API service

| Variable | Default | Description |
|---|---|---|
| `MODBUS_HOST` | `modbus-server` | Hostname of the Modbus server |
| `MODBUS_PORT` | `502` | Modbus TCP port |
| `MODBUS_UNIT` | `1` | Modbus unit ID |
| `MODBUS_TIMEOUT` | `2.0` | Connection timeout (seconds) |

### Modbus server

| Variable | Default | Description |
|---|---|---|
| `MODBUS_HOST` | `0.0.0.0` | Bind address |
| `MODBUS_PORT` | `502` | Listen port |
| `HR_SIZE` | `10000` | Holding registers count |
| `COILS_SIZE` | `2000` | Coils count |
| `DI_SIZE` | `2000` | Discrete inputs count |
| `IR_SIZE` | `2000` | Input registers count |

## Direct Modbus Access

External Modbus clients (e.g. PSS Scada) can connect directly to port **502** using standard function codes:

- **FC03** — Read Holding Registers
- **FC06** — Write Single Register
- **FC16** — Write Multiple Registers

No read-only protection is applied; all register ranges are writable.

## Dependencies

| Package | Version |
|---|---|
| Python | 3.11 |
| FastAPI | 0.115.0 |
| uvicorn | 0.30.6 |
| pymodbus | 3.6.6 |
| pydantic | 2.8.2 |
