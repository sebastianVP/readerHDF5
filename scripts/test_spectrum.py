from process_amisr14_sequence import AMISR14Sequence
from plot_spectrum_block import plot_spectrum_block

# Cargar secuencia
seq = AMISR14Sequence("/home/soporte/Documents/readerHDF5/raw_data/volts_conDECO")

# Ejecutar FFT con 64 perfiles
fft_blocks = seq.process_by_blocks("getFFT", block_size=64, nfft=64)

# Parámetros del radar
ipp_seconds = 0.005  # ejemplo: 5 ms entre perfiles
radar_freq_hz = 440e6  # ejemplo: 440 MHz

# Graficar el primer bloque (en m/s)
plot_spectrum_block(
    fft_blocks[0],
    seq.heightList,
    ipp_seconds=ipp_seconds,
    radar_freq_hz=radar_freq_hz,
    block_index=0,
    xunits="m/s"
)