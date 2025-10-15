from process_amisr14_sequence import AMISR14Sequence
from animate_spectrum_sequence import animate_spectrum_sequence

# Cargar secuencia completa
seq = AMISR14Sequence("/home/soporte/Documents/readerHDF5/raw_data/volts_sinDECO")

# Parámetros del radar
ipp_seconds = 0.005    # 5 ms entre perfiles
radar_freq_hz = 440e6  # 440 MHz

# Procesar FFT en bloques de 64 perfiles
fft_blocks = seq.process_by_blocks("getFFT", block_size=64, nfft=64)

# Animar y guardar imágenes
animate_spectrum_sequence(seq, fft_blocks,
                          ipp_seconds=ipp_seconds,
                          radar_freq_hz=radar_freq_hz,
                          block_size=64,
                          update_interval=1.0,      # cada 1 segundo
                          xunits="m/s",
                          save_frames=True,
                          output_dir="/home/soporte/Documents/readerHDF5/outputs/espectros_sinDECO")
