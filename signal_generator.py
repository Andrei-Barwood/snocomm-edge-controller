"""Generador de señales patrón 3P+N + tensión de PCC para el lazo simulado."""

from __future__ import annotations

import logging
import time
from multiprocessing import shared_memory

import numpy as np

from dsp.core import NUM_CHANNELS
from dsp.patterns import PatternSpec, generate_pattern_batch, pattern_catalog

logger = logging.getLogger("SignalGenerator")


class RealTimeSignalGenerator:
    def __init__(self, config, data_ready_event):
        self.fs = config["network"]["sampling_rate"]
        self.batch_size = config["network"]["samples_per_batch"]
        sim = config.get("simulation", {})
        catalog = pattern_catalog()
        name = sim.get("pattern", "combined_it")
        base = catalog.get(name, catalog["combined_it"])
        self.spec = PatternSpec(
            name=base.name,
            description=base.description,
            frequency_hz=config["network"]["nominal_frequency"],
            v_ln_rms=float(sim.get("voltage_ln_rms", config.get("system", {}).get("voltage_ln_rms", 230.0))),
            i1_peak=float(sim.get("i1_peak", base.i1_peak)),
            h3_peak=float(sim.get("h3_peak", base.h3_peak)),
            h5_peak=float(sim.get("h5_peak", base.h5_peak)),
            h7_peak=float(sim.get("h7_peak", base.h7_peak)),
            current_phase_lag_rad=float(sim.get("current_phase_lag_rad", base.current_phase_lag_rad)),
            noise_rms=float(sim.get("noise_rms", base.noise_rms)),
            freq_drift=bool(sim.get("freq_drift", base.freq_drift)),
        )
        self.dtype = np.float64
        self.bytes_per_batch = self.batch_size * NUM_CHANNELS * np.dtype(self.dtype).itemsize
        self.shm = shared_memory.SharedMemory(create=True, size=self.bytes_per_batch)
        self.data_ready_event = data_ready_event
        self.shared_array = np.ndarray(
            (NUM_CHANNELS, self.batch_size), dtype=self.dtype, buffer=self.shm.buf
        )
        self.t = 0.0
        self.current_freq = self.spec.frequency_hz
        self.rng = np.random.default_rng()

    def generate_batch(self):
        batch, self.current_freq, self.t = generate_pattern_batch(
            self.spec,
            self.t,
            self.fs,
            self.batch_size,
            current_freq=self.current_freq,
            rng=self.rng,
        )
        np.copyto(self.shared_array, batch)

    def run(self, stop_event):
        logger.info(
            "Generador 3P+N iniciado (%s). SHM=%s",
            self.spec.name,
            self.shm.name,
        )
        batch_duration = self.batch_size / self.fs
        try:
            while not stop_event.is_set():
                t_start = time.perf_counter()
                self.generate_batch()
                self.data_ready_event.set()
                elapsed = time.perf_counter() - t_start
                sleep_time = batch_duration - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    self.data_ready_event.clear()
        finally:
            self.shm.close()
            self.shm.unlink()
            logger.info("Generador detenido y memoria compartida liberada.")


def start_generator_process(config, stop_event, shm_name_queue, data_ready_event):
    generator = RealTimeSignalGenerator(config, data_ready_event)
    shm_name_queue.put(generator.shm.name)
    generator.run(stop_event)
