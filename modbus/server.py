import os
import logging

# Compatibilidad imports pymodbus (2.x vs 3.x)
try:
    from pymodbus.server import StartTcpServer
except Exception:
    from pymodbus.server.sync import StartTcpServer

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
    ModbusServerContext,
)
from pymodbus.device import ModbusDeviceIdentification

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("modbus-server")


def build_context():
    """
    Mapa de datos:
    - coils (0xxxx):        0..COILS_SIZE-1
    - discrete inputs (1x): 0..DI_SIZE-1
    - holding regs (4x):    0..HR_SIZE-1
    - input regs (3x):      0..IR_SIZE-1

    Nota: en pymodbus las direcciones suelen ser 0-based.
    Ej: holding address=0 equivale al 40001 en notación clásica.
    """
    COILS_SIZE = int(os.getenv("COILS_SIZE", "2000"))
    DI_SIZE    = int(os.getenv("DI_SIZE", "2000"))
    HR_SIZE    = int(os.getenv("HR_SIZE", "10000"))
    IR_SIZE    = int(os.getenv("IR_SIZE", "2000"))

    # Valores iniciales (0)
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * DI_SIZE),
        co=ModbusSequentialDataBlock(0, [0] * COILS_SIZE),
        hr=ModbusSequentialDataBlock(0, [0] * HR_SIZE),
        ir=ModbusSequentialDataBlock(0, [0] * IR_SIZE),
        zero_mode=True,  # MUY importante: direcciones 0-based coherentes
    )

    return ModbusServerContext(slaves=store, single=True)


def build_identity():
    identity = ModbusDeviceIdentification()
    identity.VendorName = "Energio"
    identity.ProductCode = "EM"
    identity.VendorUrl = "https://example.local"
    identity.ProductName = "Energio Modbus TCP Server"
    identity.ModelName = "pymodbus"
    identity.MajorMinorRevision = "1.0.0"
    return identity


def main():
    host = os.getenv("MODBUS_HOST", "0.0.0.0")
    port = int(os.getenv("MODBUS_PORT", "502"))

    context = build_context()
    identity = build_identity()

    log.info(f"Starting Modbus TCP Server on {host}:{port}")
    StartTcpServer(context=context, identity=identity, address=(host, port))


if __name__ == "__main__":
    main()