from gtts import gTTS
import vlc
import os
import time

data_path = os.path.join(os.getcwd(), "source/emg_calibration/audio_files/")

# Australian hello
tts = gTTS('hello', lang='en', tld='com.au')

audio_string = "Pull your left elbow over your head"
tts2= gTTS(audio_string, lang='en')

# Name of saved file
fn = os.path.join(data_path, 'audio_to_play.mp3')

tts2.save(fn)

p = vlc.MediaPlayer(fn)

p.play()
time.sleep(5) # need sleep to hear output
p.stop()