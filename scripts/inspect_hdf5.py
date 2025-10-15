"""
Script: inspect_hdf5.py
Autor: Alexander Valdez
Descripción:
    Este programa permite explorar la estructura interna de un archivo HDF5.
    Muestra los grupos, datasets, dimensiones, tipos de datos y atributos.
    Es útil para entender la organización de los archivos del radar AMISR-14.

Uso:
    python inspect_hdf5.py --file ruta/al/archivo.hdf5
"""

import h5py
import argparse
import os

def print_hdf5_structure(name, obj):
    """Función auxiliar para imprimir la estructura jerárquica del archivo"""
    indent = '  ' * (name.count('/') - 1)
    if isinstance(obj, h5py.Dataset):
        print(f"{indent}📊 Dataset: {name}")
        print(f"{indent}   - Forma: {obj.shape}")
        print(f"{indent}   - Tipo: {obj.dtype}")
    elif isinstance(obj, h5py.Group):
        print(f"{indent}📁 Grupo: {name}")

def inspect_hdf5_file(file_path):
    """Explora e imprime la estructura completa del archivo HDF5"""
    if not os.path.exists(file_path):
        print(f"❌ Error: El archivo '{file_path}' no existe.")
        return

    print(f"🔍 Explorando archivo: {file_path}\n{'-'*60}")

    with h5py.File(file_path, "r") as f:
        # Recorrer toda la estructura del archivo
        f.visititems(print_hdf5_structure)

        print("\n📂 Atributos globales:")
        for key, value in f.attrs.items():
            print(f"   - {key}: {value}")

    print(f"\n✅ Exploración finalizada.\n{'-'*60}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspecciona la estructura de un archivo HDF5.")
    parser.add_argument("--file", required=True, help="Ruta al archivo .hdf5")
    args = parser.parse_args()

    inspect_hdf5_file(args.file)