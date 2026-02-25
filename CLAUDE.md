# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Modbus TCP server with a REST API wrapper. Two containerized microservices communicate over a Docker bridge network (`energio_net`):

- **Modbus Server** (`modbus/server.py`) — pymodbus TCP server on port 502
- **REST API** (`api/main.py`) — FastAPI service on port 8000, acts as Modbus client

## Build & Run

```bash
# Start both services
docker compose up --build

# Start in background
docker compose up --build -d

# Stop
docker compose down
```

No test framework, linter, or CI pipeline is configured.

## Architecture

### REST API (`api/main.py`)

FastAPI app with three endpoints:
- `GET /health` — checks API and Modbus server connectivity
- `GET /read?address=N&count=M` — read holding registers (address 0-based, count 1-125)
- `POST /write` — write single holding register (body: `{address: int, value: 0-65535}`)

Connects to the Modbus server on each request, closes connection in `finally` block. Uses Pydantic models for request validation.

### Modbus Server (`modbus/server.py`)

Exposes four data blocks: coils (2000), discrete inputs (2000), holding registers (10000), input registers (2000). Sizes configurable via env vars. Uses 0-based addressing (Modbus address 40001 = address 0 in API).

Has try/except imports for pymodbus v2/v3 compatibility.

## Environment Variables

**API** (set in docker-compose.yml):
- `MODBUS_HOST` (default: "modbus-server"), `MODBUS_PORT` (502), `MODBUS_UNIT` (1), `MODBUS_TIMEOUT` (2.0)

**Modbus Server**:
- `MODBUS_HOST` ("0.0.0.0"), `MODBUS_PORT` (502), `HR_SIZE` (10000), `COILS_SIZE` (2000), `DI_SIZE` (2000), `IR_SIZE` (2000)

## Key Dependencies

- Python 3.11, FastAPI 0.115.0, pymodbus 3.6.6, Pydantic 2.8.2, Uvicorn 0.30.6
