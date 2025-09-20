import os
import glob
from obspy import read
from obspy.signal.util import _npts2nfft
from obspy.signal.cross_correlation import correlate, xcorr_max
from norma_time import normalize
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")

folder_path = r"C:\Users\ERamosP\Desktop\Proyectos\IINGEN\Valle de Mexico Zonificacion sismica\Estudios\Experimento 2025\SPAC 1"

mseed_files = glob.glob(os.path.join(folder_path, "*.mseed"))

stream = sum([read(file) for file in mseed_files], start=read(mseed_files[0])[0:0])

print(stream)

tr1 = stream[2]
tr2 = stream[5]

#Filter
for tr in [tr1, tr2]:
    tr.filter("bandpass", freqmin=0.5, freqmax=5.0,
              corners=4, zerophase=True)

#Time domain normalization
from norma_time import normalize
tr1.data = normalize(tr1.data, method="onebit")
tr2.data = normalize(tr2.data, method="onebit")

""" time = tr1.times("relative") 
plt.figure(figsize=(12, 4))
plt.plot(time, tr1.data)
plt.show() """


# Cross-correlation of two traces
# Trim to common time window
start = max(tr1.stats.starttime, tr2.stats.starttime)
end = min(tr1.stats.endtime, tr2.stats.endtime)
tr1.trim(start, end)
tr2.trim(start, end)

#Cross-correlation
cc = correlate(tr1.data, tr2.data, shift=len(tr1.data)//2)

#Time-shift
shift, value = xcorr_max(cc)
dt = shift / tr1.stats.sampling_rate
print(f"Max correlation at shift: {shift} samples")
print(f"Time lag: {dt:.4f} seconds")


#Graph
# Create time axis for cross-correlation
npts = len(cc)
time_axis = np.linspace(-npts/2, npts/2, npts) / tr1.stats.sampling_rate

# Plot
plt.figure(figsize=(10, 4))
plt.plot(time_axis, cc, label="Cross-correlation")
plt.axvline(dt, color='r', linestyle='--', label=f"Max at {dt:.2f} s")
plt.title("Cross-Correlation Between Signals")
plt.xlabel("Lag Time (s)")
plt.xlim(-10, 10)
plt.ylim(-0.1, 0.1)
plt.ylabel("Correlation Coefficient")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.ion()
plt.show(block=True)

