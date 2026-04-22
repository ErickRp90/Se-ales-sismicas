import numpy as np
import matplotlib.pyplot as plt
from obspy import read, Stream
from obspy.signal.trigger import plot_trigger
from obspy.signal.trigger import classic_sta_lta
from glob import glob

#Lectura de datos
import os
files = glob(os.path.join("C:\\Users\\ERamosP\\Desktop\\Proyectos\\IINGEN\\Arreglos\\Mixcoac\\Datos_24h_Z\\P001", "**", "*.gcf"), recursive=True)
print(f"Found {len(files)} GCF files")
print(f"Files: {files}")

signals = Stream()
for i in range(len(files)):
    file = files[i]
    try:
        st_temp = read(file, format="GCF")
        mseed_file = file.replace('.gcf', '.mseed')
        st_temp.write(mseed_file, format="MSEED")
        signals += st_temp
    except OSError as e:
        print(f"Error reading {file}: {e}")
        continue
    
    #Preprocesamiento
    # Create new figure for each signal
    plt.figure(figsize=(12, 10))
    #Plot
    t = np.arange(0, signals[i].stats.npts / signals[i].stats.sampling_rate, signals[i].stats.delta)
    plt.subplot(411)
    plt.plot(t, signals[i].data, 'k')
    plt.ylabel('Señal original [counts]')
    #Preprocesamiento
    signals[i].detrend("demean")
    signals[i].taper(max_percentage=0.05, type='cosine')
    plt.subplot(412)
    plt.plot(t, signals[i].data, 'k')
    plt.ylabel('Preprocesada [counts]')
    #Filtrado
    signals[i].filter('bandpass',freqmin=0.1,freqmax=10,corners=4,zerophase=False)
    plt.subplot(413)
    plt.plot(t, signals[i].data, 'k')
    plt.ylabel('Filtrada [counts]')

    #Correccion instrumental
    poles = [-0.14803 + 0.14803j, -0.14803 - 0.14803j, -391.95515 + 850.69303j, -391.95515 - 850.69303j,
             -2199.11486 + 0.0j, -471.23890 + 0.0j]
    zeros = [0.0 + 0.0j, 0.0 + 0.0j]
    scale_fac = 2.26590e21
    #scale_fac = 9.13e11

    # Create PAZ dictionary for instrumental correction
    paz_dict = {
        'poles': poles,
        'zeros': zeros,
        'gain': scale_fac,
        'sensitivity': 1.0
        #'sensitivity': 2390*1039501.040
    }

    # Apply instrumental correction
    signals[i].simulate(paz_remove=paz_dict, paz_simulate=None)

    #Unidades en mm/s
    signals[i].data *= 1000.0
    plt.subplot(414)
    plt.plot(t, signals[i].data, 'k')
    plt.ylabel('Corregida [mm/s]')
    plt.xlabel('Time [s]')
    #plt.ylim(-0.1, 0.1)
    
    # Save plot to JPG in data folder using the GCF filename
    gcf_filename = os.path.splitext(os.path.basename(file))[0]  # Get filename without extension
    plt.savefig(f"C:/Users/ERamosP/Desktop/Proyectos/IINGEN/Arreglos/Mixcoac/Datos_24h_Z/P001/{gcf_filename}.jpg", format='jpg', dpi=300, bbox_inches='tight')
    plt.close()  # Close the figure to avoid memory issues

    #Exportar el archivo como mseed
    signals[i].write(f"C:/Users/ERamosP/Desktop/Proyectos/IINGEN/Arreglos/Mixcoac/Datos_24h_Z/P001/{signals[i].id}.mseed", format="MSEED")

    

       