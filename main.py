import asyncio
import logging
import yaml
import time
import numpy as np

from dsp_engine import HarmonicCompensator
from scada_bridge import ModbusScadaClient

def load_config(path: str) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

async def main(data_queue=None):
    config = load_config('config.yaml')
    
    # Configurar logging
    log_level = getattr(logging, config['logging']['level'].upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config['logging']['file']),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("main")
    
    logger.info("Iniciando AHF Edge Controller...")

    # Instanciar el motor DSP
    net_config = config['network']
    compensator = HarmonicCompensator(
        fundamental_freq=net_config['fundamental_frequency'],
        sampling_rate=net_config['sampling_rate'],
        target_harmonics=[3, 5, 7]
    )
    
    # Instanciar el puente SCADA
    scada_config = config['scada']
    scada_client = ModbusScadaClient(
        host=scada_config['host'],
        port=scada_config['port'],
        unit_id=scada_config['unit_id'],
        chunk_size_registers=scada_config['chunk_size_registers']
    )
    
    samples_per_frame = net_config['samples_per_frame']
    raw_reg = scada_config['raw_waveform_register']
    comp_reg = scada_config['compensation_register']

    await scada_client.connect()
    
    frame_count = 0
    
    try:
        while True:
            try:
                # 1. Leer onda cruda
                t0 = time.perf_counter()
                raw_waveform = await scada_client.read_raw_waveform(raw_reg, samples_per_frame)
                t_read = time.perf_counter() - t0
                
                # 2. Calcular compensación
                t0 = time.perf_counter()
                comp_waveform = compensator.compute_compensation(raw_waveform)
                t_dsp = time.perf_counter() - t0
                
                # 3. Escribir onda de compensación
                t0 = time.perf_counter()
                await scada_client.write_compensation_waveform(comp_reg, comp_waveform)
                t_write = time.perf_counter() - t0
                
                frame_count += 1
                
                rms_total = np.sqrt(np.mean(raw_waveform**2))
                logger.info(f"Trama #{frame_count} | RMS Onda Cruda: {rms_total:.2f} | Tiempos(ms) - Read: {t_read*1000:.1f}, DSP: {t_dsp*1000:.1f}, Write: {t_write*1000:.1f}")

                # Enviar datos a la interfaz web
                if data_queue is not None:
                    try:
                        payload = {
                            "frame_count": frame_count,
                            "t_read_ms": t_read * 1000,
                            "t_dsp_ms": t_dsp * 1000,
                            "t_write_ms": t_write * 1000,
                            "raw_waveform": raw_waveform.tolist(),
                            "comp_waveform": comp_waveform.tolist()
                        }
                        if data_queue.full():
                            data_queue.get_nowait()
                        data_queue.put_nowait(payload)
                    except Exception as e:
                        logger.error(f"Error enrutando a WebSocket: {e}")

                # Ceder el control
                await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(f"Error en el lazo de control: {e}")
                await asyncio.sleep(1.0)
                if not scada_client.client.connected:
                    await scada_client.connect()
                    
    except asyncio.CancelledError:
        logger.info("Bucle principal cancelado.")
    finally:
        await scada_client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupción del usuario. Cerrando...")
