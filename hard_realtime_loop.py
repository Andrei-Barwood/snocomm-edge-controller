"""Lazo de procesamiento por microbloques (no hard real-time certificado)."""

from __future__ import annotations

import logging
from multiprocessing import shared_memory

import numpy as np

from dsp.core import NUM_CHANNELS, BlockDspController

logger = logging.getLogger("BlockDSP")

# Alias conservado para no romper importaciones previas.
HardRealTimeController = BlockDspController


class SharedMemoryDspLoop:
    def __init__(self, config, shm_name, data_ready_event, telemetry_queue):
        self.data_ready_event = data_ready_event
        self.telemetry_queue = telemetry_queue
        self.batch_size = config["network"]["samples_per_batch"]
        sim = config.get("simulation", {})
        self.dsp = BlockDspController(
            sampling_rate=config["network"]["sampling_rate"],
            nominal_frequency=config["network"]["nominal_frequency"],
            kp=config["pll"]["kp"],
            ki=config["pll"]["ki"],
            max_current_rms=config["hardware"]["max_current_rms"],
            voltage_ln_rms=float(
                sim.get("voltage_ln_rms", config.get("system", {}).get("voltage_ln_rms", 230.0))
            ),
            delay_samples=config["dsp"]["system_delay_samples"],
        )
        self.dtype = np.float64
        self.shm = shared_memory.SharedMemory(name=shm_name)
        self.shared_array = np.ndarray(
            (NUM_CHANNELS, self.batch_size), dtype=self.dtype, buffer=self.shm.buf
        )

    def run(self, stop_event):
        logger.info("Lazo DSP por microbloques iniciado (PLL a tensión, modelo αβ0).")
        try:
            while not stop_event.is_set():
                if not self.data_ready_event.wait(timeout=1.0):
                    continue
                self.data_ready_event.clear()
                result = self.dsp.process(self.shared_array.copy())
                if result.frame_count % 20 != 0:
                    continue
                try:
                    if self.telemetry_queue.full():
                        self.telemetry_queue.get_nowait()
                    self.telemetry_queue.put_nowait(result.to_dict())
                except Exception as exc:
                    logger.warning("Error de cola de telemetría: %s", exc)
        finally:
            self.shm.close()
            logger.info("Lazo DSP detenido.")


def start_hrt_process(config, stop_event, shm_name_queue, data_ready_event, telemetry_queue):
    shm_name = shm_name_queue.get()
    SharedMemoryDspLoop(config, shm_name, data_ready_event, telemetry_queue).run(stop_event)
