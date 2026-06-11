import asyncio
import logging
import numpy as np
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian

logger = logging.getLogger(__name__)

class ModbusScadaClient:
    def __init__(self, host: str, port: int, unit_id: int = 1, chunk_size_registers: int = 100):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.chunk_size_registers = chunk_size_registers
        self.client = AsyncModbusTcpClient(host, port=port)
        
    async def connect(self):
        """Intenta conectar al servidor Modbus con backoff exponencial."""
        attempt = 0
        while not self.client.connected:
            try:
                await self.client.connect()
                if self.client.connected:
                    logger.info(f"Conectado a SCADA en {self.host}:{self.port}")
                    break
            except Exception:
                pass
            
            attempt += 1
            wait_time = min(2 ** attempt, 30)
            logger.warning(f"Fallo al conectar. Reintentando en {wait_time} s...")
            await asyncio.sleep(wait_time)

    async def disconnect(self):
        """Cierra la conexión de forma segura."""
        if self.client.connected:
            self.client.close()
            logger.info("Desconectado de SCADA.")

    async def read_raw_waveform(self, register: int, count_floats: int) -> np.ndarray:
        """
        Lee una cantidad de floats desde el SCADA en bloques respetando el tamaño máximo del PDU.
        """
        if not self.client.connected:
            raise ConnectionError("No hay conexión con el servidor SCADA.")

        registers_to_read = count_floats * 2
        floats = []
        
        for offset in range(0, registers_to_read, self.chunk_size_registers):
            read_count = min(self.chunk_size_registers, registers_to_read - offset)
            # Asegurar que leemos pares de registros completos (un float32 = 2 reg)
            if read_count % 2 != 0:
                read_count -= 1
                if read_count == 0:
                    break

            response = await self.client.read_holding_registers(
                address=register + offset,
                count=read_count,
                slave=self.unit_id
            )
            
            if response.isError():
                raise Exception(f"Error Modbus al leer registros: {response}")
                
            decoder = BinaryPayloadDecoder.fromRegisters(
                response.registers,
                byteorder=Endian.BIG,
                wordorder=Endian.BIG
            )
            
            for _ in range(read_count // 2):
                floats.append(decoder.decode_32bit_float())

        return np.array(floats, dtype=np.float32)

    async def write_compensation_waveform(self, register: int, waveform: np.ndarray) -> None:
        """
        Escribe un array de floats al SCADA en bloques respetando el tamaño máximo del PDU.
        """
        if not self.client.connected:
            raise ConnectionError("No hay conexión con el servidor SCADA.")

        floats = waveform.astype(np.float32).tolist()
        total_floats = len(floats)
        floats_per_chunk = self.chunk_size_registers // 2

        for i in range(0, total_floats, floats_per_chunk):
            chunk = floats[i : i + floats_per_chunk]
            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
            for f in chunk:
                builder.add_32bit_float(f)
                
            payload = builder.to_registers()
            
            response = await self.client.write_registers(
                address=register + (i * 2),
                values=payload,
                slave=self.unit_id
            )
            
            if response.isError():
                raise Exception(f"Error Modbus al escribir registros: {response}")
