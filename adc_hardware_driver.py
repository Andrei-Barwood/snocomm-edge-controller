"""Marcador de posición de ADC: 7 canales en cero (Ia Ib Ic In Va Vb Vc)."""

from __future__ import annotations

import logging
import time
from multiprocessing import shared_memory

import numpy as np

from dsp.core import NUM_CHANNELS

logger = logging.getLogger("HardwareADC")


class HardwareADCReader:
    """Interfaz prevista para un DAQ real. Hoy no lee hardware."""

    def __init__(self, config, data_ready_event):
        self.fs = config["network"]["sampling_rate"]
        self.batch_size = config["network"]["samples_per_batch"]
        self.dtype = np.float64
        self.bytes_per_batch = self.batch_size * NUM_CHANNELS * np.dtype(self.dtype).itemsize
        self.shm = shared_memory.SharedMemory(create=True, size=self.bytes_per_batch)
        self.data_ready_event = data_ready_event
        self.shared_array = np.ndarray(
            (NUM_CHANNELS, self.batch_size), dtype=self.dtype, buffer=self.shm.buf
        )
        logger.info(
            "ADC marcador inicializado (ceros, %s canales). fs=%s Hz, batch=%s",
            NUM_CHANNELS,
            self.fs,
            self.batch_size,
        )

    def run(self, stop_event):
        logger.warning("Modo hardware activo: el driver entrega ceros. No hay DAQ conectado.")
        dt = self.batch_size / self.fs
        try:
            while not stop_event.is_set():
                t0 = time.perf_counter()
                self.shared_array.fill(0.0)
                self.data_ready_event.set()
                elapsed = time.perf_counter() - t0
                if elapsed < dt:
                    time.sleep(dt - elapsed)
        finally:
            logger.info("Cerrando ADC marcador.")
            self.shm.close()
            self.shm.unlink()


def start_hardware_process(config, stop_event, shm_name_queue, data_ready_event):
    driver = HardwareADCReader(config, data_ready_event)
    shm_name_queue.put(driver.shm.name)
    driver.run(stop_event)
