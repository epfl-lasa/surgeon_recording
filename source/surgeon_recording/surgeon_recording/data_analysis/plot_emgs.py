import plotly.express as px
import pandas as pd
import csv
import numpy as np
import scipy.signal as sp

emgAcquireDir = r'C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emgAcquire/'
path_to_csv = emgAcquireDir + 'mydata.csv'

emgDF = pd.read_csv(path_to_csv, sep=';', header=0, usecols=['time', 'ch1'])

print(emgDF.head())

# Check time array 

# end_time = emgDF['time'].iloc[-1]
# print(end_time)
# lin_time = np.linspace(0, end_time, len(emgDF.index))
# time_df = pd.DataFrame({'csv_time': emgDF['time'], 'lin_time': lin_time})
# print(time_df.head())
# fig = px.line(time_df)

# Convert time array ( ms to s)
correct_time = emgDF['time'] * 1e-3

# Filter current
data_current = emgDF['ch1']

fs = 1000 #approximate sampling frequency for emg
fny = fs/2 #nyquist frequency
fco = 25  #cut off frequency
rms_window = 20 #window size for rms
N = 4

[b, a] = sp.butter(N, 1.16*fco/fny)
rec_signal = abs(data_current)
butt_signal = sp.filtfilt(b, a, rec_signal)

# take enveloppe using rms windowing
rms_env = np.sqrt(np.convolve(np.square(rec_signal), np.ones(rms_window)/rms_window, mode='same'))

#PLOT to compare enveloppes, zoom on 1 part
start_zoom = 0
stop_zoom = 1000# len(emgDF.index)#1000
df = pd.DataFrame({
    'time': correct_time[start_zoom:stop_zoom],
    'rectified signal':rec_signal[start_zoom:stop_zoom],
    'Butterworth':butt_signal[start_zoom:stop_zoom],
    'RMS':rms_env[start_zoom:stop_zoom]
})
fig = px.line(df, x='time', y=['RMS', 'Butterworth'])

fig2 = px.line(x=emgDF['time'], y= emgDF['ch1'], labels={'x': 't', 'y':'ch1'})
fig.show()