import os
from typing import Annotated, List
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# Compatibilidad cliente pymodbus
try:
    from pymodbus.client import ModbusTcpClient
except Exception:
    from pymodbus.client.sync import ModbusTcpClient

app = FastAPI(
    title="Energio Modbus REST API",
    version="1.0.0",
    description="API REST para leer/escribir registros Modbus TCP de forma simple."
)

MODBUS_HOST = os.getenv("MODBUS_HOST", "modbus-server")
MODBUS_PORT = int(os.getenv("MODBUS_PORT", "502"))
MODBUS_UNIT = int(os.getenv("MODBUS_UNIT", "1"))  # Unit ID (por defecto 1)
MODBUS_TIMEOUT = float(os.getenv("MODBUS_TIMEOUT", "2.0"))


class WriteRequest(BaseModel):
    address: int = Field(ge=0, description="Dirección 0-based. Ej: 0 == 40001 (holding).")
    value: int = Field(ge=0, le=65535, description="Valor 0..65535 para holding register.")


class WriteMultipleRequest(BaseModel):
    address: int = Field(ge=0, description="Dirección inicial 0-based. Ej: 0 == 40001.")
    values: List[Annotated[int, Field(ge=0, le=65535)]] = Field(
        min_length=1,
        max_length=123,
        description="Lista de valores (0..65535) a escribir consecutivamente."
    )


def get_client() -> ModbusTcpClient:
    return ModbusTcpClient(
        host=MODBUS_HOST,
        port=MODBUS_PORT,
        timeout=MODBUS_TIMEOUT
    )


@app.get("/health")
def health():
    client = get_client()
    ok = client.connect()
    client.close()
    return {
        "api": "ok",
        "modbus_target": f"{MODBUS_HOST}:{MODBUS_PORT}",
        "modbus_connect": bool(ok),
    }


@app.get("/read")
def read_holding_registers(
    address: int = Query(..., ge=0, description="Dirección 0-based. Ej: 0 == 40001."),
    count: int = Query(1, ge=1, le=125, description="Nº de registros a leer (1..125)."),
):
    client = get_client()
    if not client.connect():
        raise HTTPException(status_code=502, detail="Failed to connect to Modbus server")

    try:
        result = client.read_holding_registers(address=address, count=count, slave=MODBUS_UNIT)
    finally:
        client.close()

    if result.isError():
        raise HTTPException(status_code=500, detail=f"Modbus read error: {result}")

    return {
        "address": address,
        "count": count,
        "unit": MODBUS_UNIT,
        "data": result.registers
    }


@app.post("/write")
def write_holding_register(req: WriteRequest):
    client = get_client()
    if not client.connect():
        raise HTTPException(status_code=502, detail="Failed to connect to Modbus server")

    try:
        result = client.write_register(address=req.address, value=req.value, slave=MODBUS_UNIT)
    finally:
        client.close()

    if result.isError():
        raise HTTPException(status_code=500, detail=f"Modbus write error: {result}")

    return {
        "unit": MODBUS_UNIT,
        "address": req.address,
        "value": req.value,
        "status": "ok"
    }


@app.post("/write-multiple")
def write_multiple_holding_registers(req: WriteMultipleRequest):
    client = get_client()
    if not client.connect():
        raise HTTPException(status_code=502, detail="Failed to connect to Modbus server")

    try:
        result = client.write_registers(
            address=req.address,
            values=req.values,
            slave=MODBUS_UNIT
        )
    finally:
        client.close()

    if result.isError():
        raise HTTPException(status_code=500, detail=f"Modbus write error: {result}")

    return {
        "unit": MODBUS_UNIT,
        "address": req.address,
        "count": len(req.values),
        "values": req.values,
        "status": "ok"
    }