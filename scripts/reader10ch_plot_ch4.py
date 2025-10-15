import h5py
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from datetime import datetime
import matplotlib.dates as mdates
import pytz  # pip install pytz

# Zona horaria local (Lima, Perú)
tz_local = pytz.timezone("America/Lima")

# Carpeta donde están los archivos HDF5
folder_path = "/mnt/DATA/AMISR14/2025/ESF/volt/10CANALES/d2025097"
# Canal a graficar
channel_to_plot = 4 # INDICAR EL CANAL

# Buscar todos los archivos que cumplen el formato
files = sorted(glob.glob(os.path.join(folder_path, "D*.hdf5")))
print("Archivos encontrados:", files)

if not files:
    raise FileNotFoundError("No se encontraron archivos con el formato D*.hdf5")

# --- Inicialización ---
all_channels = [[] for _ in range(10)]  # lista de 10 listas, una por canal
all_utctime = []
heights = None

# Leer cada archivo y concatenar
for file_path in files:
    with h5py.File(file_path, "r") as f:
        utctime = f["Data/utctime"][:]   # (Nperfiles,)
        all_utctime.append(utctime)

        # Leer los 10 canales
        for ch in range(10):
            channel_data = f[f"Data/data_pre/channel{ch:02d}"][:]  # (Nperfiles, Nalturas)
            all_channels[ch].append(channel_data)

        # Guardar las alturas (iguales en todos los archivos)
        if heights is None:
            heights = f["Metadata/heightList"][:] / 1000.0  # en km

# Concatenar en el eje tiempo (0) para cada canal
for ch in range(10):
    all_channels[ch] = np.concatenate(all_channels[ch], axis=0)

all_utctime = np.concatenate(all_utctime, axis=0)

print(f"Forma final canal {channel_to_plot:02d}:", all_channels[channel_to_plot].shape)
print("Tamaño del eje tiempo (utctime):", all_utctime.shape)

# Convertir utctime (UTC) a datetime en zona horaria local
time_labels = [
    datetime.utcfromtimestamp(t).replace(tzinfo=pytz.UTC).astimezone(tz_local)
    for t in all_utctime
]

# ---- GRAFICO SOLO CANAL 4 ----
data = all_channels[channel_to_plot]
power = np.abs(data) ** 2
power_db = 10 * np.log10(power + 1e-12)

# Estimar piso de ruido (percentil 5)
noise_floor = np.percentile(power_db, 5)
vmin = noise_floor
vmax = noise_floor + 45

# Graficar
fig, ax = plt.subplots(figsize=(14, 6), constrained_layout=True)
pcm = ax.pcolormesh(
    time_labels,
    heights,
    power_db.T,
    shading="auto",
    cmap="jet",
    vmin=vmin, vmax=vmax
)

ax.set_ylabel("Altura (km)")
ax.set_xlabel("Hora local (Lima, UTC-5)")
ax.set_title(f"RTI de Potencia en dB - Canal {channel_to_plot:02d}")

# Eje X con tiempo formateado
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=tz_local))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

# Barra de color
cbar = plt.colorbar(pcm, ax=ax, orientation="vertical")
cbar.set_label("Potencia (dB)")

plt.show()
