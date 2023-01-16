from gtts import gTTS
import vlc
import os
import time
import simpleaudio as sa

data_path ='C:\\Users\\LASA\\Documents\\Recordings\\surgeon_recording\\source\\emg_calibration\\audio_files\\'
# data_path = os.path.join(os.getcwd(), "source/emg_calibration/audio_files/")

# Australian hello
tts = gTTS('hello', lang='en', tld='com.au')

audio_string = "Pull your left elbow over your head"
tts2= gTTS(audio_string, lang='en')

# Name of saved file
fn = os.path.join(data_path, 'audio_to_play.mp3')

tts2.save(fn)

#p = vlc.MediaPlayer(fn)

# p.play()
# time.sleep(5) # need sleep to hear output
# p.stop()

short_bip_path = os.path.join(data_path, 'beep-07a.wav')
short_bip_path2 = os.path.join(data_path, 'beep-08b.wav')
long_bip_path = os.path.join(data_path, 'beep-02.wav')

wave_obj = sa.WaveObject.from_wave_file(short_bip_path)
play_obj = wave_obj.play()
play_obj.wait_done()
time.sleep(1)
wave_obj = sa.WaveObject.from_wave_file(short_bip_path)
play_obj = wave_obj.play()
play_obj.wait_done()
time.sleep(1)
wave_obj = sa.WaveObject.from_wave_file(short_bip_path)
play_obj = wave_obj.play()
play_obj.wait_done()
time.sleep(1)
wave_obj = sa.WaveObject.from_wave_file(long_bip_path)
play_obj = wave_obj.play()
play_obj.wait_done()