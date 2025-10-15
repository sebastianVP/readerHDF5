"""
Script: plot_spectrum_block.py
Autor: Alexander Valdez
Descripción:
    Grafica el espectro de potencia (power_spectrum) de un bloque FFT del radar AMISR-14.
    Eje X puede ser frecuencia Doppler (Hz o m/s), eje Y altura (km), color potencia (dB)
"""

import numpy as np
import matplotlib.pyplot as plt

C = 3e8  # velocidad de la luz (m/s)

def plot_spectrum_block(power_spectrum, heights, ipp_seconds, radar_freq_hz,
                        block_index=0, cmap="jet", xunits="m/s"):
    """
    Grafica el espectro de potencia de un bloque FFT del radar AMISR-14.

    Parámetros:
        power_spectrum : np.ndarray
            Arreglo (nCanales, nFFT, nAlturas)
        heights : np.ndarray
            Alturas (km)
        ipp_seconds : float
            Intervalo entre perfiles (segundos)
        radar_freq_hz : float
            Frecuencia de transmisión (Hz)
        block_index : int
            Índice del bloque a graficar
        cmap : str
            Paleta de colores
        xunits : str
            'hz' o 'm/s'
    """

    # Canal 0 por defecto
    data_db = 10 * np.log10(power_spectrum[0] + 1e-12)
    nfft, nalt = data_db.shape

    # Eje de frecuencias Doppler
    freqs = np.fft.fftshift(np.fft.fftfreq(nfft, d=ipp_seconds))  # Hz

    if xunits.lower() == "m/s":
        wavelength = C / radar_freq_hz
        freqs = (wavelength / 2) * freqs  # velocidad radial (m/s)
        xlabel = "Velocidad Doppler (m/s)"
    else:
        xlabel = "Frecuencia Doppler (Hz)"

    # Escala de colores
    vmin = np.percentile(data_db, 5)
    vmax = vmin + 40

    plt.figure(figsize=(10, 6))
    plt.pcolormesh(freqs, heights, data_db.T, shading="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(label="Potencia (dB)")

    plt.xlabel(xlabel)
    plt.ylabel("Altura (km)")
    plt.title(f"Espectro de Potencia Doppler - Bloque {block_index}")
    plt.tight_layout()
    plt.show()