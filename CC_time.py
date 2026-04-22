from obspy import read, Stream
import matplotlib.pyplot as plt
from obspy.signal.cross_correlation import correlate, xcorr_max
from glob import glob
import numpy as np

#Lectura de datos
import os
files1 = sorted(glob(os.path.join("C:\\Users\\ERamosP\\Desktop\\Proyectos\\IINGEN\\Arreglos\\Mixcoac\\Datos_24h_Z\\P001", "**", "*.mseed"), recursive=True))
files2 = sorted(glob(os.path.join("C:\\Users\\ERamosP\\Desktop\\Proyectos\\IINGEN\\Arreglos\\Mixcoac\\Datos_24h_Z\\P002", "**", "*.mseed"), recursive=True))
print(f"Found {len(files1)} MSEED files in P001")
print(f"Found {len(files2)} MSEED files in P002")

#Lectura de datos
signals1 = Stream()
for file in files1:
    try:
        st_temp = read(file, format="MSEED")
        signals1 += st_temp
    except OSError as e:
        print(f"Error reading {file}: {e}")
        continue

signals2 = Stream()
for file in files2:
    try:
        st_temp = read(file, format="MSEED")
        signals2 += st_temp
    except OSError as e:
        print(f"Error reading {file}: {e}")
        continue

# Merge consecutive 30-minute traces into 1-hour traces where possible
print("Merging signals1 into 1-hour segments...")
signals1.sort(keys=['starttime'])
merged_signals1 = Stream()
for i in range(0, len(signals1), 2):
    if i+1 < len(signals1):
        combined = Stream([signals1[i], signals1[i+1]])
        merged = combined.merge(method=1)  # Fill gaps with zeros if any
        merged_signals1 += merged
    else:
        merged_signals1 += signals1[i]
signals1 = merged_signals1

print("Merging signals2 into 1-hour segments...")
signals2.sort(keys=['starttime'])
merged_signals2 = Stream()
for i in range(0, len(signals2), 2):
    if i+1 < len(signals2):
        combined = Stream([signals2[i], signals2[i+1]])
        merged = combined.merge(method=1)  # Fill gaps with zeros if any
        merged_signals2 += merged
    else:
        merged_signals2 += signals2[i]
signals2 = merged_signals2

# Filter the data
print("Filtering signals1...")
for tr in signals1:
    tr.filter('bandpass', freqmin=1.0, freqmax=2.0, corners=4, zerophase=False)

print("Filtering signals2...")
for tr in signals2:
    tr.filter('bandpass', freqmin=1.0, freqmax=2.0, corners=4, zerophase=False)

#Time domain normalization
from norma_time import normalize
print("Normalizing signals1...")
for tr in signals1:
    tr.data = normalize(tr.data, method="onebit")

print("Normalizing signals2...")
for tr in signals2:
    tr.data = normalize(tr.data, method="onebit")

#Spectral normalization (whitening)
def spectral_whitening(trace, freqmin=1.0, freqmax=2.0):
    npts = trace.stats.npts
    sampling_rate = trace.stats.sampling_rate
    freqs = np.fft.rfftfreq(npts, d=1/sampling_rate)
    fft_data = np.fft.rfft(trace.data)
    
    # Create a mask for the desired frequency band
    band_mask = (freqs >= freqmin) & (freqs <= freqmax)
    
    # Apply whitening: divide by amplitude spectrum in the band
    amplitude_spectrum = np.abs(fft_data[band_mask])
    whitened_fft = np.zeros_like(fft_data)
    whitened_fft[band_mask] = fft_data[band_mask] / (amplitude_spectrum + 1e-10)  # Avoid division by zero
    
    # Inverse FFT to get back to time domain
    whitened_data = np.fft.irfft(whitened_fft, n=npts)
    return whitened_data

# Apply spectral whitening to signals1
print("Applying spectral whitening to signals1...")
for tr in signals1:
    tr.data = spectral_whitening(tr)

# Apply spectral whitening to signals2
print("Applying spectral whitening to signals2...")
for tr in signals2:
    tr.data = spectral_whitening(tr)

#Cross-correlation between corresponding files (same timestamp)
correlations = []  # List to store all correlation arrays
for i in range(min(len(signals1), len(signals2))):
    corr = correlate(signals1[i].data, signals2[i].data, signals1[i].stats.npts)
    correlations.append(corr)
    shift, value = xcorr_max(corr)
    print(f"Cross-correlation between {signals1[i].id} and {signals2[i].id}: shift={shift}, value={value}")
    
    # Plot the cross-correlation (lag -10 to 10 seconds)
    plt.figure(figsize=(10, 6))
    sampling_rate = signals1[i].stats.sampling_rate
    max_lag_samples = int(10 * sampling_rate)  # 10 seconds in samples
    npts = len(corr)
    lag_samples = np.arange(- (npts // 2), npts // 2 + 1)
    lag_seconds = lag_samples / sampling_rate
    
    # Find indices for -10 to 10 seconds
    mask = (lag_seconds >= -10) & (lag_seconds <= 10)
    plt.plot(lag_seconds[mask], corr[mask])
    plt.title(f'Cross-correlation: {signals1[i].id} vs {signals2[i].id}\nMax at shift={shift}, value={value:.3f}')
    plt.xlabel('Lag (seconds)')
    plt.ylabel('Correlation')
    plt.grid(True)
    
    # Save plot to JPG
    filename = f"cc_{i:02d}_{signals1[i].stats.starttime.strftime('%Y%m%d_%H%M')}.jpg"
    save_path = f"C:/Users/ERamosP/Desktop/Proyectos/IINGEN/Arreglos/Mixcoac/Datos_24h_Z/{filename}"
    plt.savefig(save_path, format='jpg', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved plot: {save_path}")

# Stack all correlations
print("Stacking all cross-correlations...")
# Pad correlations to the same length
max_len = max(len(c) for c in correlations)
padded_correlations = [np.pad(c, (0, max_len - len(c)), mode='constant', constant_values=0) for c in correlations]
stacked_corr = np.mean(padded_correlations, axis=0)  # Average all correlations

# Plot the stacked correlation
plt.figure(figsize=(10, 6))
sampling_rate = signals1[0].stats.sampling_rate  # Use sampling rate from first trace
npts = len(stacked_corr)
lag_samples = np.arange(- (npts // 2), npts // 2 + 1)
lag_seconds = lag_samples / sampling_rate

# Find indices for -10 to 10 seconds
mask = (lag_seconds >= -10) & (lag_seconds <= 10)
plt.plot(lag_seconds[mask], stacked_corr[mask])
plt.title(f'Stacked Cross-correlation: {len(correlations)} pairs\nBandpass 1.0-2.0 Hz')
plt.xlabel('Lag (seconds)')
plt.ylabel('Correlation')
plt.ylim(-0.1, 0.1)
plt.grid(True)

# Save stacked plot
stacked_path = "C:/Users/ERamosP/Desktop/Proyectos/IINGEN/Arreglos/Mixcoac/Datos_24h_Z/stacked.jpg"
plt.savefig(stacked_path, format='jpg', dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved stacked plot: {stacked_path}")

# Save stacked data to text file    
stacked_txt_path = "C:/Users/ERamosP/Desktop/Proyectos/IINGEN/Arreglos/Mixcoac/Datos_24h_Z/stacked.txt"
np.savetxt(stacked_txt_path, stacked_corr)
print(f"Saved stacked data: {stacked_txt_path}")


