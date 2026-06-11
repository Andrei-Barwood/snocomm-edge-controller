import asyncio
import logging
import numpy as np
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mock_scada")

# Configuración
HOST = "127.0.0.1"
PORT = 5020
UNIT_ID = 1
FUNDAMENTAL_FREQ = 50.0
SAMPLING_RATE = 12800
SAMPLES_PER_FRAME = 256

RAW_REGISTER_START = 0
COMPENSATION_REGISTER_START = 1000

async def update_waveform_task(context: ModbusServerContext):
    """
    Actualiza continuamente el DataBlock del esclavo con una nueva trama de señal.
    Simula una señal de 50 Hz con 3º (20%) y 5º (10%) armónico.
    """
    slave_id = UNIT_ID
    store = context[slave_id]
    
    t_start = 0.0
    dt = 1.0 / SAMPLING_RATE
    frame_duration = SAMPLES_PER_FRAME * dt
    
    logger.info("Iniciando generación de onda de prueba...")
    
    while True:
        # Generar vector de tiempo para esta trama
        t = np.linspace(t_start, t_start + frame_duration, SAMPLES_PER_FRAME, endpoint=False)
        t_start += frame_duration
        
        # Onda fundamental y armónicos
        fundamental = 100.0 * np.sin(2 * np.pi * FUNDAMENTAL_FREQ * t)
        h3 = 20.0 * np.sin(2 * np.pi * 3 * FUNDAMENTAL_FREQ * t) # 20% THD relativo a la fundamental
        h5 = 10.0 * np.sin(2 * np.pi * 5 * FUNDAMENTAL_FREQ * t) # 10% THD relativo a la fundamental
        
        waveform = fundamental + h3 + h5
        
        # Empaquetar a floats IEEE 754
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
        for val in waveform:
            builder.add_32bit_float(float(val))
            
        registers = builder.to_registers()
        
        # Escribir en los Holding Registers (bloque tipo 3 = Holding Registers internamente en pymodbus datastore, el offset es 0 para el datablock en este caso)
        # La convención de datablock en PyModbus es 3 = Holding Registers
        store.setValues(3, RAW_REGISTER_START, registers)
        
        # Esperar el tiempo equivalente a un frame para simular tiempo real
        await asyncio.sleep(frame_duration)

async def run_server():
    # Crear un bloque de datos lo suficientemente grande
    # 256 floats = 512 registros. Damos margen hasta 2000.
    datablock = ModbusSequentialDataBlock(0, [0] * 2000)
    
    store = ModbusSlaveContext(
        di=datablock,
        co=datablock,
        hr=datablock,
        ir=datablock,
        zero_mode=True
    )
    context = ModbusServerContext(slaves={UNIT_ID: store}, single=False)
    
    # Iniciar la tarea en segundo plano que actualiza la forma de onda
    asyncio.create_task(update_waveform_task(context))
    
    logger.info(f"Iniciando Mock SCADA Server en {HOST}:{PORT}")
    
    await StartAsyncTcpServer(
        context=context,
        address=(HOST, PORT)
    )

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Servidor SCADA detenido.")
