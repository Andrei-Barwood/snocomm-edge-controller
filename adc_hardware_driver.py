"""
Project: AHF Edge Controller
Type: Open Source
License: MIT
Owner: snocomm (prohibido venderlo)
Author: ਕਿਰਤਅਨ ਤੈਗ ਸਿਨਗਹ (Kirtan Teg Singh)
"""
import numpy as np
import time
import logging
from multiprocessing import shared_memory, Event

logger = logging.getLogger("HardwareADC")

class HardwareADCReader:
    """
    Abstracción de Hardware para lectura de un ADC real (ej. vía SPI, I2C, EtherCAT, PCIe DAQ).
    """
    def __init__(self, config, data_ready_event):
        self.fs = config['network']['sampling_rate']
        self.batch_size = config['network']['samples_per_batch']
        
        self.num_channels = 3
        self.dtype = np.float64
        self.bytes_per_batch = self.batch_size * self.num_channels * np.dtype(self.dtype).itemsize
        
        # Shared memory and sync events
        self.shm = shared_memory.SharedMemory(create=True, size=self.bytes_per_batch)
        self.data_ready_event = data_ready_event
        
        # Link a numpy array to the shared memory buffer
        self.shared_array = np.ndarray((self.num_channels, self.batch_size), dtype=self.dtype, buffer=self.shm.buf)
        
        # TODO: Inicializar hardware aquí
        # Ej: spi = spidev.SpiDev(); spi.open(0,0); spi.max_speed_hz = 1000000
        # Ej: task = nidaqmx.Task(); task.ai_channels.add_ai_voltage_chan("Dev1/ai0:2")
        logger.info(f"Hardware ADC inicializado. fs={self.fs} Hz, batch={self.batch_size}")

    def run(self, stop_event):
        logger.info(f"Iniciando lectura de bus físico DAQ/ADC... Shared Memory Name: {self.shm.name}")
        dt = self.batch_size / self.fs
        
        try:
            while not stop_event.is_set():
                t0 = time.perf_counter()
                
                # --- LECTURA HARDWARE REAL ---
                # Aquí se debería bloquear esperando a que el hardware o el DMA (Direct Memory Access)
                # haya llenado un buffer de tamaño `self.batch_size`.
                
                # Ejemplo simulado de lectura de un hardware devolviendo ceros (placeholder):
                # data_in = spi.readbytes(self.batch_size * 3 * 2) # asumiendo 16 bits por canal
                
                # Por ahora, inyectamos ceros para representar que no hay hardware real conectado
                self.shared_array[0, :] = 0.0
                self.shared_array[1, :] = 0.0
                self.shared_array[2, :] = 0.0
                
                # Notificar al HRT que hay un nuevo lote
                self.data_ready_event.set()
                
                # Simular el paso del tiempo que tomaría llenar el buffer físico a fs
                elapsed = time.perf_counter() - t0
                if elapsed < dt:
                    time.sleep(dt - elapsed)
                    
        finally:
            logger.info("Cerrando conexión de hardware ADC...")
            self.shm.close()
            self.shm.unlink()

def start_hardware_process(config, stop_event, shm_name_queue, data_ready_event):
    driver = HardwareADCReader(config, data_ready_event)
    shm_name_queue.put(driver.shm.name)
    driver.run(stop_event)
