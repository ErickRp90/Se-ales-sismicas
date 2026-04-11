from obspy import read
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
plt.show()

stream = read(r"C:\Users\ERamosP\Desktop\Proyectos\IINGEN\Valle de Mexico Zonificacion sismica\Estudios\Experimento 2025\Arreglo 1\Datos\AN02\VELOCIDAD_19-08-2025\EB007406.E_2025.08.19.12.49.25.mseed")

print(stream)

trace = stream[0]

data = trace.data
times = trace.times("timestamp")

df = pd.DataFrame({"Time":times, "Amplitude":data})

df["HH:MM:SS"] = pd.to_timedelta(df["Time"], unit="s").astype(str).str.split(".").str[0]

df.plot(x="HH:MM:SS", y="Amplitude", kind="line")
plt.title("Señal")
plt.xlabel("Tiempo")
plt.ylabel("Amplitud mm/s")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True)
plt.show()