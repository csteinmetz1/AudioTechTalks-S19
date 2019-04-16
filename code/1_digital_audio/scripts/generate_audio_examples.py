import os
import sys	
import glob 			# grab files
import resampy			# resample audio
import numpy as np		# yep
import librosa			# load audio files
import soundfile as sf 	# write audio files
import subprocess		# make command line calls

def naive_resample(data, sr, target_sr):

	step = int(sr/target_sr)
	if data.ndim > 1 and data.shape[0] > 1:	# stereo
		output = data[:,::step]
	else: 									# mono
		output = data[::step]

	return output

def peak_normalize(data, target):
    """ Peak normalize a signal.
    
    Normalize an input signal to a user specifed peak amplitude.   
    Params
    -------
    data : ndarray
        Input multichannel audio data.
    target : float
        Desired peak amplitude in dB.
    Returns
    -------
    output : ndarray
        Peak normalized output data.
    """
    # find the amplitude of the largest peak
    current_peak = np.max(np.abs(data))

    # calculate the gain needed to scale to the desired peak level
    gain = np.power(10.0, target/20.0) / current_peak
    output = gain * data
    
    # check for potentially clipped samples
    if np.max(np.abs(output)) >= 1.0:
        warnings.warn("Possible clipped samples in output.")

    return output

def sample_rate_conversion(data, sr, input_file, output_dir):

	input_filename = os.path.basename(input_file).strip(".wav")
	output_filepath = os.path.join(output_dir, input_filename)

	# Downsampling to 22.05 kHz
	data_22_05k = resampy.resample(np.reshape(data, (data.shape[1], data.shape[0])), sr, 22050)
	data_22_05k = np.reshape(data_22_05k, (data_22_05k.shape[1], data_22_05k.shape[0]))
	sf.write(output_filepath + "_16bit_22_05kHz" + ".wav", data_22_05k, 22050)

	# Downsampling to 22.05 kHz (no anti-aliasing filter)
	data_22_05k_no_aa = naive_resample(np.reshape(data, (data.shape[1], data.shape[0])), sr, 22050)
	data_22_05k_no_aa = np.reshape(data_22_05k_no_aa, (data_22_05k_no_aa.shape[1], data_22_05k_no_aa.shape[0]))
	sf.write(output_filepath + "_16bit_22_05kHz_no_aa" + ".wav", data_22_05k_no_aa, 22050)

	# Downsampling to 11.025 kHz
	data_11_025k = resampy.resample(np.reshape(data, (data.shape[1], data.shape[0])), sr, 11025)
	data_11_025k = np.reshape(data_11_025k, (data_11_025k.shape[1], data_11_025k.shape[0]))
	sf.write(output_filepath + "_16bit_11_025kHz" + ".wav", data_11_025k, 11025)

	# Downsampling to 11.025 kHz (no anti-aliasing filter)
	data_11_025k_no_aa = naive_resample(np.reshape(data, (data.shape[1], data.shape[0])), sr, 11025)
	data_11_025k_no_aa = np.reshape(data_11_025k_no_aa, (data_11_025k_no_aa.shape[1], data_11_025k_no_aa.shape[0]))
	sf.write(output_filepath + "_16bit_11_025kHz_no_aa" + ".wav", data_11_025k_no_aa, 11025)

	# Downsampling to 8 kHz
	data_8k = resampy.resample(np.reshape(data, (data.shape[1], data.shape[0])), sr, 8000)
	data_8k = np.reshape(data_8k, (data_8k.shape[1], data_8k.shape[0]))	
	sf.write(output_filepath + "_16bit_8kHz" + ".wav", data_8k, 8000)

def bit_depth_reduction(data, sr, input_file, output_dir):

	input_filename = os.path.basename(input_file).strip(".wav")
	output_filepath = os.path.join(output_dir, input_filename)

	# NOTE: We need to use SoX to perform these bit-depth reductions

	# Bit depth reduction to 8 bits (with dither)
	subprocess.call("sox '{0}' -b 8 '{1}'".format(input_file, output_filepath + "_8bit_44_1kHz.wav"), shell=True)

	# Bit depth reduction to 8 bits (no dither)
	subprocess.call("sox '{0}' -b 8 -D '{1}'".format(input_file, output_filepath + "_8bit_44_1kHz_no_dither.wav"), shell=True)

	# load audio so we can diff them and hear any differences
	data_16bit, sr = sf.read(output_filepath + "_16bit_44_1kHz.wav")
	data_8bit, sr = sf.read(output_filepath + "_8bit_44_1kHz.wav")
	data_8bit_no_dither, sr = sf.read(output_filepath + "_8bit_44_1kHz_no_dither.wav")

	
	# need to normalize for diff to work
	norm_data_16bit = peak_normalize(data_16bit, -3)
	norm_data_8bit = peak_normalize(data_8bit, -3)
	norm_data_8bit_no_dither = peak_normalize(data_8bit_no_dither, -3)

	data_diff = norm_data_16bit - norm_data_8bit
	data_diff_no_dither = norm_data_16bit - norm_data_8bit_no_dither

	sf.write(output_filepath + "_16bit_to_8bit_diff.wav", data_diff, sr)
	sf.write(output_filepath + "_16bit_to_8bit_diff_no_dither.wav", data_diff_no_dither, sr)


def sine_wave_samples(output_dir):

	fs = 44100
	f = 1000
	t = 3 

	samples = np.linspace(0, t, int(fs*t), endpoint=False)
	sine_1k = (1/(10**(12/20))) * np.sin(2 * np.pi * f * samples)

	# Normal output 
	sf.write(os.path.join(output_dir, "1k_sine_16bit_44_1kHz.wav"), sine_1k, 44100)

	# Bit depth reduction to 8 bits (with dither)
	input_filename = os.path.join(output_dir, "1k_sine_16bit_44_1kHz.wav")
	output_filename = os.path.join(output_dir, "1k_sine_8bit_44_1kHz.wav")
	subprocess.call("sox '{0}' -b 8 '{1}'".format(input_filename,  output_filename), shell=True)

	# Bit depth reduction to 8 bits (no dither)
	output_filename = os.path.join(output_dir, "1k_sine_8bit_44_1kHz_no_dither.wav")
	subprocess.call("sox '{0}' -b 8 -D '{1}'".format(input_filename, output_filename), shell=True)

	# Mix two sine waves
	sine_8k = (1/(10**(12/20))) * np.sin(2 * np.pi * 8000 * samples)
	mix = sine_1k + sine_8k

	# Normal output
	sf.write(os.path.join(output_dir, "1k+8k_sine_16bit_44_1kHz.wav"), mix, 44100)

	# Downsampling to 11.025 kHz
	mix_resamp = resampy.resample(mix, 44100, 11025)
	sf.write(os.path.join(output_dir, "1k+8k_sine_16bit_11_025kHz.wav"), mix_resamp, 11025)

	# Downsampling to 11.025 kHz (no anti-aliasing filter)
	mix_naive_resamp = naive_resample(mix, 44100, 11025)
	sf.write(os.path.join(output_dir, "1k+8k_sine_16bit_11_025kHz_no_aa.wav"), mix_naive_resamp, 11025)

def build_webpage(output_dir, input_filename):
	# eventually this will build a nice HTML page
	# that will allow you to easily demo all 
	# of the examples generated with this script
	pass

def main(input_file):
	data, sr = sf.read(input_file)
	data *= (1/(10**(1/20))) # add 1dB of headroom
	input_filename = os.path.basename(input_file).strip(".wav")
	output_dir = "example_outputs"

	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)

	# CD quality version
	sf.write(os.path.join(output_dir, input_filename + "_16bit_44_1kHz" + ".wav"), data, 44100)

	sample_rate_conversion(data, sr, input_file, output_dir)
	bit_depth_reduction(data, sr, input_file, output_dir)
	sine_wave_samples(output_dir)
	#build_webpage(output_dir, input_filename)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python generate_audio_examples.py 'path/to/audio.wav'")
	else:
		input_file = sys.argv[1]
	main(input_file)