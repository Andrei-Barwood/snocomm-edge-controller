"""
Project: AHF Edge Controller
Type: Open Source
License: MIT
Owner: snocomm (prohibido venderlo)
Author: ਕਿਰਤਅਨ ਤੈਗ ਸਿਨਗਹ (Kirtan Teg Singh)
"""
import multiprocessing as mp
import yaml
import time
import logging
import sys

from signal_generator import start_generator_process
from hard_realtime_loop import start_hrt_process
from supervisory_process import start_ts_process
from adc_hardware_driver import start_hardware_process

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MainIndustrial")

def load_config():
    with open('config_industrial.yaml', 'r') as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    
    stop_event = mp.Event()
    # Actually, Event can be passed directly but not via Manager if we want shared memory synchronization.
    # We will use mp.Event() and pass it.
    sync_event = mp.Event()
    
    shm_name_queue = mp.Queue()
    telemetry_queue = mp.Queue(maxsize=100)
    
    logger.info("Iniciando Edge Controller Industrial...")

    # Launch Signal Generator or Hardware Driver
    mode = config.get('system', {}).get('mode', 'simulation')
    if mode == "hardware":
        p_gen = mp.Process(target=start_hardware_process, args=(config, stop_event, shm_name_queue, sync_event), name="HardwareDAQProcess")
    else:
        p_gen = mp.Process(target=start_generator_process, args=(config, stop_event, shm_name_queue, sync_event), name="SignalGenProcess")
        
    p_gen.start()
    
    # Proceso Hard Real-Time (DSP / PLL / Control)
    p_hrt = mp.Process(target=start_hrt_process, args=(config, stop_event, shm_name_queue, sync_event, telemetry_queue), name="HRT_Loop")
    p_hrt.start()
    
    # Proceso de Supervisión (Modbus, Web, InfluxDB)
    p_ts = mp.Process(target=start_ts_process, args=(config, telemetry_queue), name="Supervisory")
    p_ts.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Deteniendo sistema...")
        stop_event.set()
        
        p_gen.join(timeout=2)
        p_hrt.join(timeout=2)
        p_ts.terminate() # Web server might not exit cleanly on event
        p_ts.join(timeout=2)
        logger.info("Sistema detenido de forma segura.")

if __name__ == "__main__":
    main()
