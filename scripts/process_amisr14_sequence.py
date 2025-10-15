"""
Script: process_amisr14_sequence.py
Autor: Alexander Valdez
Descripción:
    Lee múltiples archivos HDF5 del radar AMISR-14 en orden temporal,
    construye una secuencia continua de perfiles y aplica operaciones
    por bloques (por ejemplo, FFT sobre N perfiles).

Requiere: read_amisr14_class.py (de la versión anterior)
"""

import glob
import numpy as np
from read_amisr14_class import read_amisr14_file, DataOut


class AMISR14Sequence:
    """Maneja una secuencia de archivos AMISR-14 de manera ordenada y continua."""

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.files = sorted(glob.glob(f"{folder_path}/*.hdf5"))
        if not self.files:
            raise FileNotFoundError(f"No se encontraron archivos HDF5 en {folder_path}")
        self.dataOutList = []
        self.data = None
        self.utctime = None
        self.heightList = None
        self._load_all()

    def _load_all(self):
        """Carga todos los archivos secuencialmente."""
        print(f"📂 Cargando {len(self.files)} archivos desde {self.folder_path}")
        all_data = []
        all_utctime = []

        for file in self.files:
            d = read_amisr14_file(file)
            self.dataOutList.append(d)
            all_data.append(d.data)
            all_utctime.append(d.utctime)

        # Concatenar en orden temporal
        self.data = np.concatenate([d for d in all_data], axis=1)  # (canales, perfiles_total, alturas)
        self.utctime = np.concatenate([u for u in all_utctime])
        self.heightList = self.dataOutList[0].heightList

        # Asegurar que los archivos sean consecutivos en tiempo
        diffs = np.diff(self.utctime)
        if np.max(diffs) > 10:  # umbral arbitrario de 10 seg entre archivos
            print("⚠️ Advertencia: se detectaron saltos de tiempo entre archivos no consecutivos.")

        print(f"✅ Datos concatenados: {self.data.shape}")

    # -------------------------------------------------------------
    # 🔹 Operaciones por bloques
    # -------------------------------------------------------------

    def process_by_blocks(self, operation, block_size, **kwargs):
        """
        Aplica una operación a bloques de perfiles.

        Parámetros:
            operation: str -> 'getFFT', 'getPower', etc.
            block_size: int -> número de perfiles por bloque
            kwargs -> parámetros adicionales de cada operación

        Devuelve:
            Lista de resultados de cada bloque
        """
        n_profiles = self.data.shape[1]
        print(f"\n⚙️ Ejecutando operación '{operation}' en bloques de {block_size} perfiles...")
        results = []

        i = 0
        while i < n_profiles:
            end = i + block_size
            if end > n_profiles:
                # si el bloque excede, ya no hay más archivos disponibles
                # simplemente rompe (también se podría implementar relleno)
                end = n_profiles

            block = self.data[:, i:end, :]
            if block.shape[1] < block_size:
                print("⚠️ Bloque incompleto al final, omitido.")
                break

            if operation == "getFFT":
                res = self._compute_fft(block, **kwargs)
            elif operation == "getPower":
                res = np.mean(np.abs(block) ** 2, axis=1)
            else:
                raise ValueError(f"Operación '{operation}' no reconocida")

            results.append(res)
            i += block_size

        print(f"✅ {len(results)} bloques procesados.")
        return results

    def _compute_fft(self, block, nfft=64):
        """Calcula la FFT a lo largo del eje de perfiles para un bloque."""
        fft_res = np.fft.fftshift(np.fft.fft(block, n=nfft, axis=1), axes=1)
        power_spectrum = np.abs(fft_res) ** 2
        return power_spectrum


# -------------------------------------------------------------
# Ejemplo de uso
# -------------------------------------------------------------
if __name__ == "__main__":
    folder = "/mnt/DATA/AMISR14/2025/ESF"
    seq = AMISR14Sequence(folder)

    # Ejecutar FFT sobre bloques de 64 perfiles
    fft_blocks = seq.process_by_blocks("getFFT", block_size=64, nfft=64)

    # Mostrar resumen
    print(f"\nFFT de primer bloque -> forma: {fft_blocks[0].shape}")
