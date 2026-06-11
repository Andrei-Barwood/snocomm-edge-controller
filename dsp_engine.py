import numpy as np
import logging

logger = logging.getLogger(__name__)

class HarmonicCompensator:
    def __init__(self, fundamental_freq: float, sampling_rate: float, target_harmonics: list[int]):
        """
        :param fundamental_freq: Frecuencia fundamental en Hz (ej. 50).
        :param sampling_rate: Tasa de muestreo en Hz.
        :param target_harmonics: Lista de órdenes armónicos a cancelar (ej. [3, 5, 7]).
        """
        self.fundamental_freq = fundamental_freq
        self.sampling_rate = sampling_rate
        self.target_harmonics = target_harmonics
        
        # Frecuencias exactas a buscar
        self.target_freqs = [fundamental_freq * h for h in target_harmonics]

    def compute_compensation(self, waveform: np.ndarray) -> np.ndarray:
        """
        Calcula la onda de compensación para cancelar los armónicos objetivo.
        :param waveform: Array 1-D con las muestras de la señal cruda (corriente o tensión).
        :return: Array 1-D de la misma longitud con la señal de compensación.
        """
        if not isinstance(waveform, np.ndarray):
            raise TypeError("La señal debe ser un array de NumPy.")
        
        n = len(waveform)
        if n == 0:
            raise ValueError("El array de la señal está vacío.")

        # Aplicar ventana Hanning para reducir el leakage espectral
        window = np.hanning(n)
        windowed_waveform = waveform * window

        # Calcular la FFT para señales reales
        spectrum = np.fft.rfft(windowed_waveform)
        
        # Vector de frecuencias
        freqs = np.fft.rfftfreq(n, d=1.0/self.sampling_rate)
        
        # Crear un espectro vacío para la señal de compensación
        comp_spectrum = np.zeros_like(spectrum)

        # Identificar y aislar los armónicos objetivo
        for target_freq in self.target_freqs:
            # Encontrar el índice de la frecuencia más cercana
            idx = np.argmin(np.abs(freqs - target_freq))
            
            # Invertir fase (multiplicar por -1) conservando magnitud
            comp_spectrum[idx] = spectrum[idx] * -1.0

        # Reconstruir la señal en el dominio del tiempo
        comp_waveform = np.fft.irfft(comp_spectrum, n=n)

        # La señal reconstruida representa la compensación que debe aplicarse.
        return comp_waveform
