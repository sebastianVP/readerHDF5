"""
Script: read_amisr14_class.py
Autor: Alexander Valdez
Descripción:
    Lee datos del radar AMISR-14 (formato HDF5) y los almacena
    en un objeto estructurado de la clase DataOut.

Estructura del objeto:
    dataOut.data        -> ndarray de forma (nCanales, nPerfiles, nAlturas)
    dataOut.utctime     -> ndarray (nPerfiles,)
    dataOut.heightList  -> ndarray (nAlturas,)

Uso:
    python read_amisr14_class.py --file ./D0001.hdf5
"""

import h5py
import numpy as np
import argparse
from datetime import datetime
import pytz

# Zona horaria local (Lima, Perú)
tz_local = pytz.timezone("America/Lima")


class DataOut:
    """Clase contenedora de los datos del radar AMISR-14."""
    def __init__(self):
        self.data = None          # ndarray (nCanales, nPerfiles, nAlturas)
        self.utctime = None       # ndarray (nPerfiles,)
        self.heightList = None    # ndarray (nAlturas,)
        self.time_labels = None   # lista de datetimes (hora local)
        self.info = {}            # metadatos (n_canales, n_perfiles, n_alturas)

    def resumen(self):
        """Imprime un resumen general del contenido."""
        print("\n📦 Resumen del objeto dataOut:")
        print(f"   - Canales:  {self.info.get('n_channels', '?')}")
        print(f"   - Perfiles: {self.info.get('n_profiles', '?')}")
        print(f"   - Alturas:  {self.info.get('n_heights', '?')}")
        if self.utctime is not None:
            print(f"   - Primer timestamp (local): {self.time_labels[0].strftime('%Y-%m-%d %H:%M:%S')}")
        print("------------------------------------------------------------")


def read_amisr14_file(file_path):
    """Lee un archivo HDF5 del radar AMISR-14 y devuelve un objeto DataOut."""
    print(f"\n📂 Leyendo archivo: {file_path}")

    dataOut = DataOut()

    with h5py.File(file_path, "r") as f:
        # Leer canal principal (por ahora solo channel00)
        ch0 = f["Data/data_pre/channel00"][:]  # (nPerfiles, nAlturas)
        n_profiles, n_heights = ch0.shape

        # Preparar estructura 3D (nCanales, nPerfiles, nAlturas)
        n_channels = 1
        dataOut.data = np.zeros((n_channels, n_profiles, n_heights), dtype=ch0.dtype)
        dataOut.data[0, :, :] = ch0

        # Leer tiempos y alturas
        dataOut.utctime = f["Data/utctime"][:]
        dataOut.heightList = f["Metadata/heightList"][:]

    # Convertir tiempos UTC a hora local
    dataOut.time_labels = [
        datetime.utcfromtimestamp(t).replace(tzinfo=pytz.UTC).astimezone(tz_local)
        for t in dataOut.utctime
    ]

    # Guardar metadatos
    dataOut.info = {
        "n_channels": n_channels,
        "n_profiles": n_profiles,
        "n_heights": n_heights,
    }

    dataOut.resumen()
    return dataOut


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lee datos del radar AMISR-14 en un objeto DataOut.")
    parser.add_argument("--file", required=True, help="Ruta al archivo .hdf5")
    args = parser.parse_args()

    dataOut = read_amisr14_file(args.file)