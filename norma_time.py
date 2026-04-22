import  numpy as np

def normalize(signal, method="onebit"):
    if method == "onebit":
        return np.where(signal > 0, 1.0, np.where(signal < 0, -1.0, 0.0))
    if method == "running_absolute_mean":
        window_size = 100  # Adjust as needed
        abs_signal = np.abs(signal)
        running_mean = np.convolve(abs_signal, np.ones(window_size)/window_size, mode='same')
        return signal / (running_mean + 1e-10)  # Avoid division by zero
    else:
        raise ValueError("Unknown normalization method")