# 📡 Radar AMISR-14 – Análisis y Visualización de Datos

Este conjunto de scripts permite procesar y visualizar la información proveniente del radar **AMISR-14**.  
Los programas están orientados a generar **gráficos de potencia**, tanto a partir de **data cruda** como de **data decodificada**, mediante espectros y diagramas RTI (Range-Time Intensity).

---

## 🧠 Descripción general

Los scripts permiten realizar dos tipos principales de análisis:

### 1. **Espectros (Spectra)**
- Se aplican transformadas rápidas de Fourier (**FFT**) sobre los perfiles de tiempo.
- Es necesario definir el número de puntos en la FFT (`N_FFT`) según la resolución deseada.
- El resultado es un gráfico espectral que muestra la distribución de potencia en función de la frecuencia Doppler.

### 2. **RTI (Range-Time Intensity)**
- Se calcula la **potencia** de las señales en función del rango y del tiempo.
- Los resultados de cada bloque se **concatenan de forma consecutiva** para construir una visualización continua.
- El resultado es un mapa de intensidad de potencia (RTI), útil para observar la evolución temporal de las irregularidades ionosféricas.

---

## 📂 Estructura general

<pre> 
├── Readme.md ← Este archivo
├── ouputs/ ← Resultados de espectros Doppler (potencia vs altura-frecuencia)
├── scripts/ ← Scripts principales del procesamiento
│ ├── animate_spectrum_sequence.py ← Anima y guarda secuencias de espectros Doppler
│ ├── inspect_hdf5.py ← Inspecciona el contenido de un archivo HDF5
│ ├── plot_spectrum_block.py ← Grafica un bloque FFT (espectro individual)
│ ├── potencia_rti_esf.py ← Calcula y genera RTI de potencia (Eco Spread F)
│ ├── process_amisr14_sequence.py ← Clase principal de procesamiento por bloques
│ ├── read_amisr14_class.py ← Lector de archivos HDF5 en estructura unificada
│ ├── reader10ch_rti_ch4.py ← Ejemplo: RTI usando canal 4 (10 canales)
│ ├── test_animate_spectrum.py ← Ejemplo de animación de espectros Doppler
│ └── test_spectrum.py ← Ejemplo de espectro estático (bloque único) </pre>
