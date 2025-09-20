import  numpy as np

def normalize(signal, method="onebit"):
    if method == "onebit":
        return np.where(signal > 0, 1.0, np.where(signal < 0, -1.0, 0.0))
    else:
        raise ValueError("Unknown normalization method")