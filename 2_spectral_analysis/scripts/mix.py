import os
import sys	
import glob 					# grab files
import numpy as np				# yep
import seaborn as sns			# make plots look pretty
import soundfile as sf 			# write audio files
import matplotlib.pyplot as plt	# make plots
from scipy import signal		# correlate function

output_dir = "audio"
if not os.path.isdir(output_dir):
	os.makedirs(output_dir)

fs = 44100
f1 = 440.0
f2 = 660.0
t = 3 

samples = np.linspace(0, t, int(fs*t), endpoint=False)
a4 = (1/(10**(6/20))) * np.sin(2 * np.pi * f1 * samples)
e4 = (1/(10**(6/20))) * np.sin(2 * np.pi * f2 * samples)
mix = a4 + e4

# plot pure tones and mix
sns.set()
sns.set_style("white")
sns.set_style("ticks")

fig, ax = plt.subplots(figsize=(10, 4))
plt_samp = 800

# Mixed sine waves plots 
#-----------------------------------------------------
def time_domain_mix():
	ax.plot(samples[:plt_samp], a4[:plt_samp])
	plt.ylabel('Amplitude')
	plt.xlabel('Time [sec]')
	plt.grid()
	sns.despine()
	plt.axis('off')
	plt.savefig("../figs/440Hz_sine_wave.svg")
	plt.cla()

	ax.plot(samples[:plt_samp], e4[:plt_samp])
	plt.ylabel('Amplitude')
	plt.xlabel('Time [sec]')
	plt.grid()
	sns.despine()
	plt.axis('off')
	plt.savefig("../figs/660Hz_sine_wave.svg")
	plt.cla()

	ax.plot(samples[:plt_samp], a4[:plt_samp]+e4[:plt_samp])
	plt.ylabel('Amplitude')
	plt.xlabel('Time [sec]')
	plt.grid()
	sns.despine()
	plt.axis('off')
	plt.savefig("../figs/440Hz+660Hz_sine_wave.svg")
	plt.cla()

# Basic cross-correlation example
#-----------------------------------------------------
def basic_xcorr():

	if not os.path.isdir("../figs/corr/ex"):
		os.makedirs("../figs/corr/ex")

	fig = plt.figure(figsize=(10, 8))
	ax1 = fig.add_subplot(2,1,1)
	ax2 = fig.add_subplot(2,1,2)
	for freq in [200.0, 440.0]:
		xcorr_lags = 800
		e4 = (1/(10**(6/20))) * np.sin(2 * np.pi * freq * samples)
		xcorr = signal.correlate(a4[:xcorr_lags], e4[:xcorr_lags],
			mode='full') / xcorr_lags	

		for lag in np.arange(0, xcorr_lags, 20):
			ax1.plot(samples[:xcorr_lags], a4[:xcorr_lags])
			ax1.plot(samples[:xcorr_lags]+(lag/fs), e4[:xcorr_lags])
			ax1.set_ylim(-0.6, 0.6)
			ax1.set_xlim(0, xcorr_lags/fs)
			ax2.plot(xcorr[xcorr_lags:xcorr_lags+lag], 'teal')
			ax2.set_ylim(-0.2, 0.2)
			ax2.set_xlim(0, xcorr_lags)
			ax2.fill_between(np.arange(lag), 0, 
				xcorr[xcorr_lags:xcorr_lags+lag], facecolor='lightcyan')
			plt.ylabel('Correlation')
			plt.xlabel('Lag [samples]')
			sns.despine()
			#ax1.axis('off')
			#ax2.axis('off')
			plt.savefig("../figs/corr/ex/440Hz_{}_corr_lag_{}.svg".format(freq, lag))
			ax1.clear()
			ax2.clear()


# Cross-correlation -> Fourier Transform example
#-----------------------------------------------------
def xcorr_to_ft():

	if not os.path.isdir("../figs/corr/ft"):
		os.makedirs("../figs/corr/ft")

	fig = plt.figure(figsize=(10, 8))
	ax1 = fig.add_subplot(2,1,1)
	ax2 = fig.add_subplot(2,1,2)
	fourier = []
	freqs = np.arange(20, 1020, 20)
	for idx, freq in enumerate(freqs):
		xcorr_lags = 800
		kernal = (1/(10**(6/20))) * np.sin(2 * np.pi * freq * samples)
		xcorr = signal.correlate(a4[:xcorr_lags], kernal[:xcorr_lags],
			mode='full') / xcorr_lags

		ax1.plot(xcorr[xcorr_lags:], 'teal')
		ax1.set_ylim(-0.2, 0.2)
		ax1.set_xlim(0, xcorr_lags)
		ax1.fill_between(np.arange(xcorr_lags-1), 0, 
			xcorr[xcorr_lags:], facecolor='lightcyan')
		fourier.append(np.sum(np.abs(xcorr)))
		ax2.plot(freqs[:len(fourier)], fourier, color='firebrick', zorder=1)
		ax2.scatter(freq, fourier[idx], color='maroon', zorder=10)
		ax2.text(800, 50, "f = {}".format(freq), verticalalignment='center')
		ax2.set_ylim(0, 70)
		ax2.set_xlim(20, 1020)
		ax2.set_ylabel('Magnitude')
		ax2.set_xlabel('Frequency [Hz]')
		sns.despine()
		plt.savefig("../figs/corr/ft/440Hz_{}_corr.svg".format(freq))
		ax1.clear() 
		ax2.clear()

# Back to our original example (Cross-correlation -> Fourier Transform)
#-----------------------------------------------------
def mix_ft():

	if not os.path.isdir("../figs/corr/mix"):
		os.makedirs("../figs/corr/mix")


	fig = plt.figure(figsize=(10, 8))
	ax1 = fig.add_subplot(2,1,1)
	ax2 = fig.add_subplot(2,1,2)
	fourier = []
	freqs = np.arange(20, 1010, 10)
	for idx, freq in enumerate(freqs):
		xcorr_lags = 800
		kernal = (1/(10**(6/20))) * np.sin(2 * np.pi * freq * samples)
		xcorr = signal.correlate(mix[:xcorr_lags], kernal[:xcorr_lags],
			mode='full') / xcorr_lags

		ax1.plot(xcorr[xcorr_lags:], 'teal')
		ax1.set_ylim(-0.2, 0.2)
		ax1.set_xlim(0, xcorr_lags)
		ax1.fill_between(np.arange(xcorr_lags-1), 0, xcorr[xcorr_lags:], facecolor='lightcyan')
		fourier.append(np.sum(np.abs(xcorr[xcorr_lags:])))
		ax2.plot(freqs[:len(fourier)], fourier, color='firebrick', zorder=1)
		ax2.scatter(freq, fourier[idx], color='maroon', zorder=10)
		ax2.text(800, 30, "f = {} Hz".format(freq), verticalalignment='center')
		ax2.set_ylim(0, 40)
		ax2.set_xlim(20, 1010)
		sns.despine()
		plt.savefig("../figs/corr/mix/mix_{}_corr.svg".format(freq))
		ax1.clear() 
		ax2.clear()

def piano_ft():
	if not os.path.isdir("../figs/corr/piano"):
		os.makedirs("../figs/corr/piano")

	# load piano audio
	piano, rate = sf.read("../audio/piano-note.wav")
	piano = piano[:10000]

	fig = plt.figure(figsize=(10, 8))
	ax1 = fig.add_subplot(2,1,1)
	ax2 = fig.add_subplot(2,1,2)
	fourier = []
	freqs = np.arange(20, 1010, 10)
	for idx, freq in enumerate(freqs):
		xcorr_lags = 800
		kernal = np.sin(2 * np.pi * freq * samples)
		xcorr = signal.correlate(piano[:xcorr_lags], kernal[:xcorr_lags], mode='full')

		ax1.plot(xcorr[xcorr_lags:], 'teal')
		ax1.set_ylim(-0.05, 0.05)
		ax1.set_xlim(0, xcorr_lags)
		ax1.fill_between(np.arange(xcorr_lags-1), 0, xcorr[xcorr_lags:], facecolor='lightcyan')
		fourier.append(np.sum(np.abs(xcorr[xcorr_lags:])))
		ax2.plot(freqs[:len(fourier)], fourier, color='firebrick', zorder=1)
		ax2.scatter(freq, fourier[idx], color='maroon', zorder=10)
		ax2.text(800, 10, "f = {} Hz".format(freq), verticalalignment='center')
		ax2.axvline(x=130)
		ax2.set_ylim(0, 18)
		ax2.set_xlim(20, 1010)
		sns.despine()
		plt.savefig("../figs/corr/piano/piano_{}_corr.svg".format(freq))
		ax1.clear() 
		ax2.clear()

# save out audio examples
def save_audio_files():
	sf.write(os.path.join(output_dir, "a4_440Hz.wav"), a4, 44100)
	sf.write(os.path.join(output_dir, "e4_660Hz.wav"), e4, 44100)
	sf.write(os.path.join(output_dir, "a4+e4.wav"), mix, 44100)

#basic_xcorr()
#xcorr_to_ft()
#mix_ft()
piano_ft()