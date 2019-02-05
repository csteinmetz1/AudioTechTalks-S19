import os
import sys	
import glob 					# grab files
import imageio					# create animated gifs
import cairosvg					# convert svg to png
import numpy as np				# yep
import seaborn as sns			# make plots look pretty
import soundfile as sf 			# write audio files
import matplotlib.pyplot as plt	# make plots
from scipy import signal		# correlate function
from scipy import fftpack		# fft functions

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

def pitch_shift():
	print("Pitch shifting in frequency domain example...")
	if not os.path.isdir("../figs/corr/shift"):
		os.makedirs("../figs/corr/shift/svg")
		os.makedirs("../figs/corr/shift/png")

	piano, rate = sf.read("../audio/piano-note.wav")
	piano = piano[:len(samples)]
	frame_size = 1024
	n_frames = int(len(samples) / frame_size)

	fig = plt.figure(figsize=(10, 8))
	ax1 = fig.add_subplot(2,1,1)
	ax2 = fig.add_subplot(2,1,2)

	#fft_full = np.fft.rfft(piano)

	shift = 1
	output_frames = []
	for idx in range(n_frames):
		frame = piano[idx*frame_size:idx*frame_size+frame_size]
		fft_frame = np.fft.rfft(frame)
		shifted_fft = np.roll(fft_frame, shift)
		shifted_fft[0:shift] = 0
		ifft = np.fft.irfft(shifted_fft)
		output_frames.append(ifft)

	mag = np.abs(fft_frame)/frame_size
	shift_mag = np.abs(shifted_fft)/frame_size

	output = np.concatenate(output_frames)
	print(output.shape)

	sf.write(os.path.join(output_dir, "piano-shifted.wav"), output, 44100)

	k = np.arange(int(frame_size/2))
	freqs = k * (fs/1024)

	ax1.loglog(freqs, mag[:int(frame_size/2)], color='firebrick')
	ax2.set_ylim(0.00001, 0.2)
	ax2.set_xlim(20, 22050)

	ax2.loglog(freqs, shift_mag[:int(frame_size/2)], color='firebrick')
	ax2.set_ylim(0.00001, 0.2)
	ax2.set_xlim(20, 22050)
	sns.despine()
	plt.savefig("../figs/corr/shift/svg/shift_piano_fft.svg")
	ax1.clear() 
	ax2.clear()
	
	# turn into png ...
	#svg_frames = glob.glob("../figs/corr/fft/svg/*.svg")
	#png_dir = "../figs/corr/fft/png"
	#for frame in svg_frames:
	#   frame_name = os.path.basename(frame).replace(".svg", ".png")
	#	cairosvg.svg2png(url=frame, write_to=os.path.join(png_dir, frame_name))

def td_to_fd():
	print("Time domain to frequency domain example...")
	if not os.path.isdir("../figs/corr/fft"):
		os.makedirs("../figs/corr/fft/svg")
		os.makedirs("../figs/corr/fft/png")

	piano, rate = sf.read("../audio/piano-note.wav")
	piano = piano[:len(samples)]
	frame_size = 1024
	n_frames = int(len(samples) / frame_size)

	fig = plt.figure(figsize=(10, 8))
	ax1 = fig.add_subplot(2,1,1)
	ax2 = fig.add_subplot(2,1,2)

	for idx in np.arange(n_frames):

		frame = piano[idx*frame_size:idx*frame_size+frame_size]
		fft = fftpack.fft(frame)/frame_size
		mag = np.abs(fft)

		k = np.arange(int(frame_size/2))
		freqs = k * (fs/1024)

		ax1.plot(frame)
		ax1.set_ylim(-0.6, 0.6)
		ax1.set_xlim(0, 1024)

		ax2.loglog(freqs, mag[:int(frame_size/2)], color='firebrick')
		ax2.set_ylim(0.00001, 0.2)
		ax2.set_xlim(20, 22050)
		sns.despine()
		plt.savefig("../figs/corr/fft/svg/{}_piano_fft.svg".format(idx))
		ax1.clear() 
		ax2.clear()
	
	# turn into png ...
	svg_frames = glob.glob("../figs/corr/fft/svg/*.svg")
	png_dir = "../figs/corr/fft/png"
	for frame in svg_frames:
		frame_name = os.path.basename(frame).replace(".svg", ".png")
		cairosvg.svg2png(url=frame, write_to=os.path.join(png_dir, frame_name))

	# ... then into gif
	png_frames = sorted(glob.glob("../figs/corr/fft/png/*.png"), key=find_idx)
	output_file = "../figs/corr/fft.gif"
	duration = 0.1 #* len(png_frames)
	create_gif(png_frames, output_file, duration)

# Basic sliding cross-correlation example
#-----------------------------------------------------
def basic_slide():
	print("Basic sliding cross-correlation example...")
	if not os.path.isdir("../figs/corr/slide"):
		os.makedirs("../figs/corr/slide/svg")
		os.makedirs("../figs/corr/slide/png")

	fig = plt.figure(figsize=(10, 4))
	ax1 = fig.add_subplot(1,1,1)
	for freq in [440.0]:
		xcorr_lags = 800
		e4 = (1/(10**(6/20))) * np.sin(2 * np.pi * freq * samples)
		xcorr = signal.correlate(a4[:xcorr_lags], e4[:xcorr_lags],
			mode='full') / xcorr_lags	

		for idx, lag in enumerate(np.arange(0, xcorr_lags, 20)):
			ax1.plot(samples[:xcorr_lags], a4[:xcorr_lags])
			ax1.plot(samples[:xcorr_lags]+(lag/fs), e4[:xcorr_lags])
			ax1.set_ylim(-0.6, 0.6)
			ax1.set_xlim(0, xcorr_lags/fs)
			plt.ylabel('Correlation')
			plt.xlabel('Lag [samples]')
			sns.despine()
			ax1.axis('off')
			plt.savefig("../figs/corr/slide/svg/{0}_440Hz_{1}Hz_corr_lag_{2}.svg".format(idx, freq, lag))
			ax1.clear()

	# turn into png ...
	svg_frames = glob.glob("../figs/corr/slide/svg/*.svg")
	png_dir = "../figs/corr/slide/png"
	for frame in svg_frames:
		frame_name = os.path.basename(frame).replace(".svg", ".png")
		cairosvg.svg2png(url=frame, write_to=os.path.join(png_dir, frame_name))

	# ... then into gif
	png_frames = sorted(glob.glob("../figs/corr/slide/png/*.png"), key=find_idx)
	output_file = "../figs/corr/slide.gif"
	duration = 0.2 #* len(png_frames)
	create_gif(png_frames, output_file, duration)

# Basic cross-correlation example
#-----------------------------------------------------
def basic_xcorr():
	print("Basic cross-correlation example...")
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
			plt.savefig("../figs/corr/ex/440Hz_{}Hz_corr_lag_{}.svg".format(freq, lag))
			ax1.clear()
			ax2.clear()

# Cross-correlation -> Fourier Transform example
#-----------------------------------------------------
def xcorr_to_ft():
	print("Cross-correlation to Fourier Transform...")
	if not os.path.isdir("../figs/corr/ft"):
		os.makedirs("../figs/corr/ft/svg")
		os.makedirs("../figs/corr/ft/png")

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
		ax2.text(320, 50, "A4 = 440 Hz", verticalalignment='center')
		ax2.axvline(x=440, color='lightslategrey')
		ax2.text(freq+8, fourier[idx]+2, "f = {} Hz".format(freq), verticalalignment='center')
		ax2.set_ylim(0, 70)
		ax2.set_xlim(20, 1020)
		ax2.set_ylabel('Magnitude')
		ax2.set_xlabel('Frequency [Hz]')
		sns.despine()
		plt.savefig("../figs/corr/ft/svg/{}_440Hz_{}_corr.svg".format(idx, freq))
		ax1.clear() 
		ax2.clear()

	# turn into png ...
	svg_frames = glob.glob("../figs/corr/ft/svg/*.svg")
	png_dir = "../figs/corr/ft/png"
	for frame in svg_frames:
		frame_name = os.path.basename(frame).replace(".svg", ".png")
		cairosvg.svg2png(url=frame, write_to=os.path.join(png_dir, frame_name))

	# ... then into gif
	png_frames = sorted(glob.glob("../figs/corr/ft/png/*.png"), key=find_idx)
	output_file = "../figs/corr/ft.gif"
	duration = 0.3 #* len(png_frames)
	create_gif(png_frames, output_file, duration)

# Back to our original example (Cross-correlation -> Fourier Transform)
#-----------------------------------------------------
def mix_ft():
	print("Analyze mixed sinusoids with FT...")
	if not os.path.isdir("../figs/corr/mix"):
		os.makedirs("../figs/corr/mix/svg")
		os.makedirs("../figs/corr/mix/png")

	fig = plt.figure(figsize=(10, 12))
	ax1 = fig.add_subplot(3,1,1)
	ax2 = fig.add_subplot(3,1,2)
	ax3 = fig.add_subplot(3,1,3)
	fourier = []
	freqs = np.arange(20, 1000, 20)
	for idx, freq in enumerate(freqs):
		xcorr_lags = 2000
		kernal = np.sin(2 * np.pi * freq * samples)
		xcorr = signal.correlate(mix[:xcorr_lags], kernal[:xcorr_lags], mode='full')
		xcorr /= xcorr.shape[0]

		ax1.plot(mix[:int(xcorr_lags/2)])
		ax1.plot(kernal[:int(xcorr_lags/2)])
		ax2.plot(xcorr[xcorr_lags:], 'teal')
		ax2.set_ylim(-0.2, 0.2)
		ax2.set_xlim(0, xcorr_lags)
		ax2.fill_between(np.arange(xcorr_lags-1), 0, xcorr[xcorr_lags:], facecolor='lightcyan')
		fourier.append(np.sum(np.abs(xcorr[xcorr_lags:])))
		ax3.plot(freqs[:len(fourier)], fourier, color='firebrick', zorder=1)
		ax3.scatter(freq, fourier[idx], color='maroon', zorder=10)
		ax3.text(310, 80, "A4 = 440 Hz", verticalalignment='center')
		ax3.text(530, 80, "E4 = 660 Hz", verticalalignment='center')
		ax3.axvline(x=440, color='lightslategrey')
		ax3.axvline(x=660, color='lightslategrey')
		ax3.text(freq+8, fourier[idx]+2, "f = {} Hz".format(freq), verticalalignment='center')
		ax3.set_ylim(0, 100)
		ax3.set_xlim(20, 1010)
		sns.despine()
		plt.savefig("../figs/corr/mix/svg/{}_mix_{}_corr.svg".format(idx, freq))
		ax1.clear()
		ax2.clear() 
		ax3.clear()

	# turn into png ...
	svg_frames = glob.glob("../figs/corr/mix/svg/*.svg")
	png_dir = "../figs/corr/mix/png"
	for frame in svg_frames:
		frame_name = os.path.basename(frame).replace(".svg", ".png")
		cairosvg.svg2png(url=frame, write_to=os.path.join(png_dir, frame_name))

	# ... then into gif
	png_frames = sorted(glob.glob("../figs/corr/mix/png/*.png"), key=find_idx)
	output_file = "../figs/corr/mix.gif"
	duration = 0.3 #* len(png_frames)
	create_gif(png_frames, output_file, duration)

def piano_ft():
	print("Analyze piano using 'Fourier' Transform...")
	if not os.path.isdir("../figs/corr/piano"):
		os.makedirs("../figs/corr/piano/svg")
		os.makedirs("../figs/corr/piano/png")

	# load piano audio
	piano, rate = sf.read("../audio/piano-note.wav")
	piano = piano[:len(samples)]

	fig = plt.figure(figsize=(10, 8))
	ax1 = fig.add_subplot(2,1,1)
	ax2 = fig.add_subplot(2,1,2)
	fourier = []
	freqs = np.arange(20, 1000, 20)
	for idx, freq in enumerate(freqs):
		xcorr_lags = 2000
		kernal = np.sin(2 * np.pi * freq * samples)
		xcorr = signal.correlate(piano[:xcorr_lags], kernal[:xcorr_lags], mode='full')
		xcorr /= xcorr.shape[0] 
		ax1.plot(xcorr[xcorr_lags:], 'teal')
		ax1.set_ylim(-0.1, 0.1)
		ax1.set_xlim(0, xcorr_lags)
		ax1.fill_between(np.arange(xcorr_lags-1), 0, 
			xcorr[xcorr_lags:], facecolor='lightcyan')
		fourier.append(np.sum(np.abs(xcorr[xcorr_lags:])))
		ax2.plot(freqs[:len(fourier)], fourier, color='firebrick', zorder=1)
		ax2.scatter(freq, fourier[idx], color='maroon', zorder=10)
		ax2.text(125, 35, "C4 = 261 Hz", verticalalignment='center')
		ax2.axvline(x=261, color='lightslategrey')
		ax2.text(freq+3, fourier[idx]+2, "f = {} Hz".format(freq), verticalalignment='center')		
		ax2.set_ylim(0, 40)
		ax2.set_xlim(20, 1010)
		sns.despine()
		plt.savefig("../figs/corr/piano/svg/{}_piano_{}_corr.svg".format(idx, freq))
		ax1.clear() 
		ax2.clear()
	
	# turn into png ...
	svg_frames = glob.glob("../figs/corr/piano/svg/*.svg")
	png_dir = "../figs/corr/piano/png"
	for frame in svg_frames:
		frame_name = os.path.basename(frame).replace(".svg", ".png")
		cairosvg.svg2png(url=frame, write_to=os.path.join(png_dir, frame_name))

	# ... then into gif
	png_frames = sorted(glob.glob("../figs/corr/piano/png/*.png"), key=find_idx)
	output_file = "../figs/corr/piano.gif"
	duration = 0.1 #* len(png_frames)
	create_gif(png_frames, output_file, duration)

def create_gif(filenames, output_file, duration):
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(output_file, images, duration=duration)

def find_idx(filename):
	return int(os.path.basename(filename).split('_')[0])

# save out audio examples
def save_audio_files():
	sf.write(os.path.join(output_dir, "a4_440Hz.wav"), a4, 44100)
	sf.write(os.path.join(output_dir, "e4_660Hz.wav"), e4, 44100)
	sf.write(os.path.join(output_dir, "a4+e4.wav"), mix, 44100)

#basic_slide()
#basic_xcorr()
#xcorr_to_ft()
#mix_ft()
#piano_ft()
pitch_shift()
#td_to_fd()