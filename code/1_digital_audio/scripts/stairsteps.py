import sys
import matplotlib.pyplot as plt
import numpy as np
 
def format_func(value, tick_number):
    # find number of multiples of pi/2
    N = int(np.round(2 * value / np.pi))
    if N == 0:
        return "0"
    elif N == 1:
        return r"$\pi/2$"
    elif N == 2:
        return r"$\pi$"
    elif N % 2 > 0:
        return r"${0}\pi/2$".format(N)
    else:
        return r"${0}\pi$".format(N // 2)

# generate sine wave
n = np.arange(0, 32)
x = np.linspace(0, 2*np.pi, num=32)
values = np.sin(x)

# plot the 'analog' sine wave
fig, ax = plt.subplots()
ax.plot(x, values, color='r')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.xaxis.set_major_formatter(plt.FuncFormatter(forma t_func))
ax.yaxis.grid() 
plt.tight_layout()
plt.savefig('analog_plot.svg')

# quantize the audio data
bins = np.array([0.0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 8.0])*(2/7)
x_digital = np.digitize(values + 1.0, bins, right=True)

# make a stairstep plot of the discrete data
fig1, ax1 = plt.subplots()
ax1.plot(n, (values+1.0)*(7/2), color='gray')
ax1.step(n, x_digital-1, color='r')
ax1.set_ylim([0,8])
ax1.yaxis.grid() 
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
plt.tight_layout()
plt.savefig('stairstep_plot.svg')

# make stem plot of the discrete data
fig2, ax2 = plt.subplots()
(markers, stemlines, baseline) = plt.stem(n, x_digital-1)
plt.setp(baseline, color='k', zorder=1)
plt.setp(stemlines, color='gray', zorder=1)
plt.setp(markers, color='r', zorder=10)
ax2.set_ylim([0,8])
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.yaxis.grid() 
plt.tight_layout()
plt.savefig('stem_plot.svg')
