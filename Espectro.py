import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from obspy import read, read_inventory
from obspy.io.xseed import Parser
from obspy.signal import PPSD
from obspy.core.inventory.inventory import read_inventory

from scipy.fft import fft, rfft
from scipy.fft import fftfreq, rfftfreq
#import plotly.graph_objs as go
#from plotly.subplots import make_subplots

#with open("C:/Users/ERamosP/Desktop/Proyectos/Programacion/Python/Datos gcf/merge.txt", 'r') as file:
#    content = file.read()
#print(content)

#sig = np.loadtxt("C:/Users/ERamosP/Desktop/Proyectos/Programacion/Python/Datos gcf/merge.txt")

#plt.plot(sig)
#plt.show()

st = read("C:/Users/ERamosP/Desktop/Proyectos/Programacion/Python/Datos gcf/20240107_0000-p010z.gcf")
st.detrend()
st.plot()
#sig2.spectrogram()
sig = st[0]
#sigdata = sig.data

#Remove response.
#inv = read_inventory("C:/Users/ERamosP/Desktop/Proyectos/Programacion/Python/Señales sismicas/p010z.xml")
#pre_filt = (0.05, 0.1, 45, 50)
#sig.remove_response(inventory=inv, pre_filt=pre_filt, output='DISP', water_level=60, plot=True)


st1 = read("C:/Users/ERamosP/Desktop/Proyectos/Programacion/Python/Datos gcf/2019-07-17-0358-51S.NSN___003")
st1.plot()
tacz = st1[0]
tacz.plot()
#tacz.spectrogram(log=True)








#PSSD
inv = read_inventory("C:/Users/ERamosP/Desktop/Proyectos/Programacion/Python/Señales sismicas/P010.xml")
ppsd = PPSD(sig.stats, metadata=inv)
ppsd.add(sig2)




#Fourier transform
fourier = rfft(sigdata)

plt.plot(np.abs(fourier))
#plt.show()

#Calculate N/2 to normalize the FFT output
N = len(sigdata)
normalize = N/2

# Plot the normalized FFT (|Xk|)/(N/2)
plt.plot(np.abs(fourier)/normalize)
plt.ylabel('Amplitude')
plt.xlabel('Samples')
plt.title('Normalized FFT Spectrum')
#plt.show()

# Get the frequency components of the spectrum
sampling_rate = 100.0 # It's used as a sample spacing
frequency_axis = rfftfreq(N, d=1.0/sampling_rate)
norm_amplitude = np.abs(fourier)/normalize
# Plot the results
plt.plot(frequency_axis, norm_amplitude, linewidth=0.1)
plt.xlabel('Frequency[Hz]')
plt.ylabel('Amplitude')
plt.title('Spectrum')
plt.xscale('log')
plt.xlim(0.1, 100)
plt.ylim(0, 500)
plt.show()

#PSSD for noise
