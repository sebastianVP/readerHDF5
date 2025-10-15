"""
Script: animate_spectrum_sequence.py
Autor: Alexander Valdez
Descripción:
    Anima y guarda los espectros de potencia Doppler (FFT) del radar AMISR-14.

    - Izquierda: Espectro Doppler (frecuencia/velocidad vs altura)
    - Derecha: Power profile (potencia promedio vs altura)
    - Actualiza cada `update_interval` segundos
    - Guarda cada frame como imagen PNG en 'output_dir'
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import pytz
import os

C = 3e8  # velocidad de la luz (m/s)


def _edges_from_centers(centers):
    """Construye bordes (edges) a partir de valores centrados (centers)."""
    diffs = np.diff(centers)
    inner_edges = centers[:-1] + diffs / 2.0
    first_edge = centers[0] - diffs[0] / 2.0
    last_edge = centers[-1] + diffs[-1] / 2.0
    return np.concatenate([[first_edge], inner_edges, [last_edge]])


def animate_spectrum_sequence(seq, fft_blocks, ipp_seconds, radar_freq_hz,
                              block_size=64, update_interval=1.0,
                              xunits="m/s", cmap="jet",
                              save_frames=True,
                              output_dir="./outputs/espectros"):
    """
    Anima los bloques de espectro Doppler y guarda cada frame como imagen PNG.

    Parámetros:
        seq : AMISR14Sequence
        fft_blocks : list[np.ndarray]
        ipp_seconds : float
        radar_freq_hz : float
        block_size : int
        update_interval : float (segundos)
        xunits : str ('hz' o 'm/s')
        cmap : str
        save_frames : bool (True para guardar cada frame)
        output_dir : str (ruta de destino para las imágenes)
    """

    heights = np.asarray(seq.heightList)
    tz_local = pytz.timezone("America/Lima")

    # --- Eje Doppler ---
    nfft = fft_blocks[0].shape[1]
    freqs = np.fft.fftshift(np.fft.fftfreq(nfft, d=ipp_seconds))

    if xunits.lower() == "m/s":
        wavelength = C / radar_freq_hz
        freqs = (wavelength / 2) * freqs
        xlabel = "Velocidad Doppler (m/s)"
    else:
        xlabel = "Frecuencia Doppler (Hz)"

    # --- Calcular bordes para pcolormesh ---
    freq_edges = _edges_from_centers(freqs)
    height_edges = _edges_from_centers(heights)

    # --- Crear carpeta de salida ---
    if save_frames:
        os.makedirs(output_dir, exist_ok=True)
        print(f"📂 Carpeta de salida: {os.path.abspath(output_dir)}")

    # --- Crear figura con dos subgráficos (3:1 de proporción) ---
    fig = plt.figure(figsize=(12, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=[3, 1], wspace=0.1)

    # Gráfico principal (espectro Doppler)
    ax_spec = fig.add_subplot(gs[0, 0])
    init_data = np.zeros((len(heights), len(freqs)))
    pcm = ax_spec.pcolormesh(freq_edges, height_edges, init_data,
                             shading="flat", cmap=cmap, vmin=-80, vmax=-40)
    cbar = plt.colorbar(pcm, ax=ax_spec, label="Potencia (dB)")
    title = ax_spec.set_title("Espectro Doppler - Inicializando...")
    ax_spec.set_xlabel(xlabel)
    ax_spec.set_ylabel("Altura (km)")

    # Gráfico lateral (Power Profile)
    ax_prof = fig.add_subplot(gs[0, 1], sharey=ax_spec)
    power_line, = ax_prof.plot(np.zeros_like(heights), heights, color='orange', lw=2)
    ax_prof.set_xlabel("Potencia Promedio (dB)")
    ax_prof.grid(True, alpha=0.3)
    ax_prof.tick_params(labelleft=False)  # evita duplicar etiquetas de altura

    # --- Función de actualización ---
    def update(frame_idx):
        block = fft_blocks[frame_idx]  # (nCanales, nFFT, nAlturas)
        power_db = 10 * np.log10(np.abs(block[0]) + 1e-12)  # canal 0
        vmin = np.percentile(power_db, 5)
        vmax = vmin + 40
        pcm.set_clim(vmin, vmax)
        pcm.set_array(power_db.T.ravel())

        # Power profile (promedio por altura)
        power_profile = np.mean(power_db, axis=0)
        power_line.set_xdata(power_profile)
        ax_prof.set_xlim(np.min(power_profile) - 2, np.max(power_profile) + 2)

        # Marca de tiempo local
        start_idx = frame_idx * block_size
        end_idx = min(start_idx + block_size, len(seq.utctime))
        mid_time = np.mean(seq.utctime[start_idx:end_idx])
        local_time = datetime.utcfromtimestamp(mid_time).replace(
            tzinfo=pytz.UTC).astimezone(tz_local)
        timestamp = local_time.strftime("%Y-%m-%d %H:%M:%S")

        title.set_text(f"Espectro Doppler - {timestamp} (Lima)")

        # Guardar frame como imagen
        if save_frames:
            filename = os.path.join(output_dir, f"spectrum_block_{frame_idx:04d}.png")
            fig.savefig(filename, dpi=150, bbox_inches="tight")
            print(f"💾 Guardado: {filename}")

        return [pcm, power_line, title]

    # --- Crear animación ---
    ani = animation.FuncAnimation(
        fig, update,
        frames=len(fft_blocks),
        interval=update_interval * 1000,
        blit=False, repeat=False
    )

    plt.tight_layout()
    plt.show()
