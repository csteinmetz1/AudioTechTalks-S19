# Spectral Analysis
This contains the resources for my [talk on spectral analysis](). Check in the scripts directory to find scripts for generating the plots and audio examples. 

## Try it yourself
You can run the same tests I show in my presentation or in my [blogpost]() on your own audio files.

To do so you need to first get an audio file stored as a .wav file at 16 bit 44.1 kHz. If you attempt to use any other kind of file the examples will not work correctly (even if you do not receive any error messages.)

Clone this repo
```
git clone https://github.com/csteinmetz1/AudioTechTalks-S19
```

Change into the proper directory
```
cd 2_spectral_analysis/scripts
```

Install proper python dependancies (this works with Python 3)
```
pip install -r requirements.txt
```

Run the python script with your .wav file as input
```
python generate_audio_examples.py path/to/audio.wav
```

This will create a new directory with all of the output samples called `example_outputs`.