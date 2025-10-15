"""
1. ESTE PROGRAMA LEE LOS ARCHIVOS CON EXTENSION hdf5
2. LOS ORDENA POR NOMBRE 0,1,2,4,...
3. Extrae la data de (perfiles,alturas), lista de alturas  y marca de tiempo
4. Concatena la data
5. Calcula la potencia
6. Genera RTI
7. Piso de ruido 5%
8. Potencia maxima para paleta de colores dbmin +40
9. Marca de tiempo eje x local time.
"""
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
folder_path = "./"   # <- cámbialo si es necesario

# Buscar todos los archivos que cumplen el formato
files = sorted(glob.glob(os.path.join(folder_path, "D*.hdf5")))

print("Archivos encontrados:", files)

all_channels = []
all_utctime = []
heights = None

# Leer cada archivo y concatenar
for file_path in files:
    with h5py.File(file_path, "r") as f:
        channel = f["Data/data_pre/channel00"][:]   # (Nperfiles, Nalturas)
        utctime = f["Data/utctime"][:]             # (Nperfiles,)
        
        all_channels.append(channel)
        all_utctime.append(utctime)
        
        # Guardar las alturas (iguales en todos los archivos)
        if heights is None:
            heights = f["Metadata/processingHeaderObj/heightList"][:] / 1000.0  # en km

# Concatenar en el eje 0 (perfiles)
all_channels = np.concatenate(all_channels, axis=0)
all_utctime = np.concatenate(all_utctime, axis=0)

print("Forma final de la matriz concatenada:", all_channels.shape)
print("Tamaño del eje tiempo (utctime):", all_utctime.shape)

# Convertir utctime (UTC) a datetime en zona horaria local
time_labels = [
    datetime.utcfromtimestamp(t).replace(tzinfo=pytz.UTC).astimezone(tz_local) 
    for t in all_utctime
]

# Calcular potencia en dB
power = np.abs(all_channels)**2
power_db = 10 * np.log10(power + 1e-12)

# Estimar piso de ruido (percentil bajo) UN CLASICO :)
noise_floor = np.percentile(power_db, 5)
vmin = noise_floor
vmax = noise_floor + 40   # puedes cambiar a +50 si quieres más rango

print(f"Piso de ruido estimado: {noise_floor:.2f} dB")
print(f"Escala de colores: vmin={vmin:.2f}, vmax={vmax:.2f}")

# ----- GRAFICO RTI DE POTENCIA EN dB -----
plt.figure(figsize=(12,6))
plt.pcolormesh(time_labels,
               heights,
               power_db.T,
               shading="auto",
               cmap="jet",
               vmin=vmin, vmax=vmax)

plt.colorbar(label="Potencia (dB)")
plt.xlabel("Hora local (Lima, UTC-5)")
plt.ylabel("Altura (km)")
plt.title("RTI de Potencia en dB (archivos concatenados, hora local)")

# Formato bonito del eje X (solo hora:minuto)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=tz_local))
plt.gcf().autofmt_xdate()

plt.show()
