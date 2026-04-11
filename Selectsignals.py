import numpy as np
import matplotlib.pyplot as plt
from obspy import read, Stream
from obspy.signal.trigger import plot_trigger
from obspy.signal.trigger import classic_sta_lta
from glob import glob

#Lectura de datos
import os
files = glob(os.path.join("C:\\Users\\ERamosP\\Desktop\\Datos\\AN28G\\an28z2", "*.mseed"))
print(f"Found {len(files)} MSEED files")
print(f"Files: {files}")

if len(files) == 0:
    print("ERROR: No MSEED files found. Check the path exists and contains .mseed files")
else:
    st2 = Stream()
    for file in files:
        st_temp = read(file, format="MSEED")
        st2 += st_temp
    st2.merge()

ste = st2[0]

#Preprocesamiento
ste2 = ste.copy()
ste2.detrend("demean")
ste2.taper(max_percentage=0.05, type='cosine')

#tacz.filter("bandpass",0.1,1,0.1,corners=4,zerophase=False)
ste2_filt = ste2.copy()
ste2_filt.filter('bandpass',freqmin=0.1,freqmax=20,corners=4,zerophase=False)

#Correccion instrumental
poles = [-0.14803 + 0.14803j, -0.14803 - 0.14803j, -391.95515 + 850.69303j, -391.95515 - 850.69303j,
          -2199.11486 + 0.0j, -471.23890 + 0.0j]
zeros = [0.0 + 0.0j, 0.0 + 0.0j]
scale_fac = 2.27774e21
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
ste2_corr = ste2_filt.copy()
ste2_corr.simulate(paz_remove=paz_dict, paz_simulate=None)

#Unidades en mm/s
ste2_corr.data *= 1000.0

#Exportar el archivo como mseed
ste2_corr.write("C:/Users/ERamosP/Desktop/Datos/AN28G/an28z2/an28z2.mseed", format="MSEED")

#Plot
t = np.arange(0, ste.stats.npts / ste.stats.sampling_rate, ste.stats.delta)
plt.subplot(411)
plt.plot(t, ste.data, 'k')
plt.ylabel('Señal original [counts]')
plt.subplot(412)
plt.plot(t, ste2.data, 'k')
plt.ylabel('Preprocesada [counts]')
plt.subplot(413)
plt.plot(t, ste2_filt.data, 'k')
plt.ylabel('Filtrada [counts]')
plt.subplot(414)
plt.plot(t, ste2_corr.data, 'k')
plt.ylabel('Corregida [mm/s]')
plt.xlabel('Time [s]')
plt.ylim(-0.5, 0.5)
#plt.suptitle(ste.stats.starttime)
plt.show()


#Espectrograma
ste2_corr.plot()
ste2_corr.spectrogram()


#Implementar el algoritmo sta/lta
#df = ste_filt.stats.sampling_rate
# set the STA=0.5 seconds, LTA=2.0 seconds
#cft = classic_sta_lta(ste_filt.data, int(0.1 * df), int(0.6 * df))
# set the trigger threshold=1.0, detrigger threshold=0.07
#plot_trigger(ste_filt, cft, 4.0, 0.05)