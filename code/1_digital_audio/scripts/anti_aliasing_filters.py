import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# 44.1 kHz AA filter
b1 = signal.firwin(20, 22000, window=('kaiser', 8), fs=44100)
w1, h1 = signal.freqz(b1, worN=2056)
f1 = (w1 / (2 * np.pi)) * 44100

# 96 kHz AA filter
b2 = signal.firwin(20, 47000, window=('kaiser', 8), fs=96000)
w2, h2 = signal.freqz(b2)
f2 = (w2 / (2 * np.pi)) * 96000

fig, ax = plt.subplots()
plt.title('Anti-aliasing filter frequency responses')
ax.plot(f1, 20 * np.log10(abs(h1)), 'blue')
ax.plot(f2, 20 * np.log10(abs(h2)), 'red')
ax.axvline(x=22050, color='k')
plt.text(23000, -15, "22050 Hz", rotation=90, verticalalignment='center')
ax.axvline(x=48000, color='k')
plt.text(48500, -15, "48000 Hz", rotation=90, verticalalignment='center')
ax.set_xlim(0, 52000)
ax.set_ylim(-30, 3)
plt.ylabel('Amplitude [dB]', color='k')
plt.xlabel('Frequency [Hz]')

plt.grid()
plt.savefig("aa_filters.svg")