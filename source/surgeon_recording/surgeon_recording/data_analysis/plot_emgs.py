import plotly.express as px
import pandas as pd
import csv
import numpy as np
import scipy.signal as sp

data_dir = r'C:/Users/LASA/Documents/Recordings/surgeon_recording/test_data/02-12-2022/test_1/'
path_to_mydata = data_dir + 'mydata.csv'
path_to_emg = data_dir + 'emg.csv'

mydataDF = pd.read_csv(path_to_mydata, sep=';', header=0, usecols=['time', 'ch1'])
emgDF = pd.read_csv(path_to_emg, usecols=['relative_time', 'emg0'])

# CHANGE THIS VALUE FOR EACH DATASET
time_offset =  3.786581
print(emgDF.head())

# Check time array 
# end_time = emgDF['time'].iloc[-1]
# print(end_time)
# lin_time = np.linspace(0, end_time, len(emgDF.index))
# time_df = pd.DataFrame({'csv_time': emgDF['time'], 'lin_time': lin_time})
# print(time_df.head())
# fig = px.line(time_df)

# Convert time array ( ms to s)
correct_time = mydataDF['time'] * 1e-3

# Filter current - EMG
data_current = emgDF['emg0']
data_current_control = mydataDF['ch1']

fs = 1000 #approximate sampling frequency for emg
fny = fs/2 #nyquist frequency
fco = 25  #cut off frequency
rms_window = 20 #window size for rms
N = 4

[b, a] = sp.butter(N, 1.16*fco/fny)
rec_signal = abs(data_current)
rec_signal_ctrl = abs(data_current_control)
butt_signal = sp.filtfilt(b, a, rec_signal)
butt_signal_ctrl = sp.filtfilt(b, a, rec_signal_ctrl)

# take enveloppe using rms windowing
rms_env = np.sqrt(np.convolve(np.square(rec_signal), np.ones(rms_window)/rms_window, mode='same'))
rms_env_ctrl = np.sqrt(np.convolve(np.square(rec_signal_ctrl), np.ones(rms_window)/rms_window, mode='same'))

#PLOT to compare enveloppes, zoom on 1 part
start_zoom = 0
stop_zoom = len(emgDF.index)#1000

df = pd.DataFrame({
    'name': 'emg recorder',
    'time': emgDF['relative_time'].iloc[start_zoom:stop_zoom],
    'rectified signal':rec_signal[start_zoom:stop_zoom],
    'Butterworth':butt_signal[start_zoom:stop_zoom],
    'RMS':rms_env[start_zoom:stop_zoom]
})

start_zoom = 0
stop_zoom = len(mydataDF.index)
df_ctrl = pd.DataFrame({ 
    'name': 'my data',
    'time': correct_time[start_zoom:stop_zoom] - time_offset,
    'rectified signal':rec_signal_ctrl[start_zoom:stop_zoom],
    'Butterworth CTRL':butt_signal_ctrl[start_zoom:stop_zoom],
    'RMS CTRL':rms_env_ctrl[start_zoom:stop_zoom]
})

df_both = pd.concat([df, df_ctrl])
fig = px.line(df_both, x='time', y='rectified signal', color='name')

# fig = px.line(df_ctrl, x='time CTRL', y=['rec CTRL', 'RMS CTRL'])
# fig2 = px.line(df, x='time', y=['rectified signal', 'RMS'])

fig.show()
# fig2.show()