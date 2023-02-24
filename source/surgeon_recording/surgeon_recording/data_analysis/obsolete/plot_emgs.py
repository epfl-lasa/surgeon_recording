import plotly.express as px
import pandas as pd
import csv
import numpy as np
import scipy.signal as sp
import matplotlib.pyplot as plt
import os
from scipy import interpolate

data_dir = r'C:/Users/LASA/Documents/Recordings/surgeon_recording/test_data/20-12-2022/calibration_torstein/'
# data_dir = r'C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emgAcquire/'
path_to_mydata = data_dir + 'mydata.csv'
path_to_emg = data_dir + 'emg.csv'

channel = 'ch1'

mydataDF = pd.read_csv(path_to_mydata, sep=';', header=0, usecols=['time [ms]', 'absolute time [s]', channel])
emgDF = pd.read_csv(path_to_emg, usecols=['relative_time', 'absolute_time', 'emg0'])

# Clip EMG values
emgDF['emg0'].clip(-8000, 8000, inplace=True)
mydataDF[channel].clip(-8000, 8000, inplace=True)

# CHANGE THIS VALUE FOR EACH DATASET (time diffesrence between mydata and emg recordings - FOR PLOT)
time_offset = 6.08244
# test 1 12 - 37.346283
# test 4 09 - 4.2611013
# test 3 09 - 2.133789
# test 2 09 - 3.677729
# test 1 09 - 18.587729
# test 5 07 - 7.0849691
# test 4 07 - 4.47602 #
# test2 07 - 10.78141
# test 1 07 - 10.67141 
# test1 02 - 3.72224 # seconds

#print(emgDF.head())


# Check time array 
# end_time = emgDF['time'].iloc[-1]
# print(end_time)
# lin_time = np.linspace(0, end_time, len(emgDF.index))
# time_df = pd.DataFrame({'csv_time': emgDF['time'], 'lin_time': lin_time})
# print(time_df.head())
# fig = px.line(time_df)

# Convert time array ( ms to s)
correct_time = mydataDF['time [ms]'] * 1e-3

# Interpolate data to deal with packet loss
end_time =emgDF['relative_time'].iloc[-2]
print(end_time)
sr_freq = 1000
nb_samples = int(sr_freq*end_time)
time_array = np.linspace(0, end_time, nb_samples)

rec_time_array = np.linspace(0, end_time, len(emgDF['relative_time'].iloc[:-2]))
s = interpolate.InterpolatedUnivariateSpline(rec_time_array, emgDF['emg0'].iloc[:-2])
data_interp = s(time_array)
print("SHAPES :", np.shape(emgDF['emg0']), np.shape(data_interp))

# interp control
start_idx = 500 # remove bad data at start of recording 
start_time = mydataDF['absolute time [s]'].iloc[start_idx]
end_time =  mydataDF['absolute time [s]'].iloc[-1] #mydataDF['time [ms]'].iloc[-1] * 1e-3 # will be end_abs - start_abs
duration = end_time - start_time
print("Conpare durations : ", duration, end_time-mydataDF['absolute time [s]'].iloc[0], mydataDF['time [ms]'].iloc[-1] * 1e-3 )
sr_freq = 1500
nb_samples = int(sr_freq*duration)
time_array_ctrl = np.linspace(0, duration, nb_samples)

rec_time_array = np.linspace(0, duration, len(mydataDF.index[start_idx:]))
# rec_time_array = correct_time[start_idx:]
s = interpolate.InterpolatedUnivariateSpline(np.array(rec_time_array), mydataDF[channel].iloc[start_idx:])
ctrl_data_interp = s(time_array_ctrl)
print("SHAPES :", np.shape(mydataDF[channel]), np.shape(ctrl_data_interp))
## More points raw than interpolated -> probably due to weird data density on start of emgAcquire

print("number fo samples vs estimated:", len(emgDF.index), nb_samples)

# Filter current - EMG
data_current = emgDF['emg0'].iloc[:-1]
data_current_control = mydataDF[channel]

# fig, ax1 = plt.subplots()

# ax1.plot(time_array_ctrl)
# ax1.plot(rec_time_array)
# plt.show()

# Filter EMG 
fs = 1000 #approximate sampling frequency for emg
fny = fs/2 #nyquist frequency
fco = 25  #cut off frequency
rms_window = 20 #window size for rms
N = 4

[b, a] = sp.butter(N, 1.16*fco/fny)
rec_signal = abs(data_current)
rec_signal_ctrl = abs(data_current_control)
butt_signal = sp.filtfilt(b, a, rec_signal)
butt_signal_interp = sp.filtfilt(b, a, abs(data_interp))

# Filter ctrl wiht 1500 SR
fs = 1500 #approximate sampling frequency for emg
fny = fs/2 #nyquist frequency
fco = 25  #cut off frequency
rms_window = 20 #window size for rms
N = 4

[b, a] = sp.butter(N, 1.16*fco/fny)
butt_signal_ctrl = sp.filtfilt(b, a, rec_signal_ctrl)
butt_signal_interp_ctrl = sp.filtfilt(b, a, abs(ctrl_data_interp))

# take enveloppe using rms windowing
rms_env = np.sqrt(np.convolve(np.square(rec_signal), np.ones(rms_window)/rms_window, mode='same'))
rms_env_ctrl = np.sqrt(np.convolve(np.square(rec_signal_ctrl), np.ones(rms_window)/rms_window, mode='same'))
rms_env_interp_ctrl = np.sqrt(np.convolve(np.square(abs(ctrl_data_interp)), np.ones(rms_window)/rms_window, mode='same'))

# Interpolate rms only
rms_interp = np.sqrt(np.convolve(np.square(abs(data_interp)), np.ones(rms_window)/rms_window, mode='same'))

# s = interpolate.InterpolatedUnivariateSpline(rec_time_array, rms_env)
# rms_interp = s(time_array)

#PLOT to compare enveloppes, zoom on 1 part
start_zoom = 0
stop_zoom = len(emgDF.index)-10#1000

df = pd.DataFrame({
    'name': 'emg recorder',
    'time': emgDF['absolute_time'].iloc[start_zoom:stop_zoom], # emgDF['relative_time'].iloc[start_zoom:stop_zoom],
    'rectified signal':rec_signal[start_zoom:stop_zoom],
    'Butterworth':butt_signal[start_zoom:stop_zoom],
    'RMS':rms_env[start_zoom:stop_zoom] #rms_env[start_zoom:stop_zoom]
})

start_zoom = 0
stop_zoom = len(time_array)-10#1000

df_interp = pd.DataFrame({
    'name': 'Interpolated emg recorder',
    'time': time_array[start_zoom:stop_zoom],
    'rectified signal': abs(data_interp[start_zoom:stop_zoom]),
    'Butterworth':butt_signal_interp[start_zoom:stop_zoom],
    'RMS':rms_interp[start_zoom:stop_zoom] #rms_env[start_zoom:stop_zoom]
})

start_zoom = 0
stop_zoom = 60000# len(mydataDF.index)
df_ctrl = pd.DataFrame({ 
    'name': 'my data',
    'time': correct_time[start_zoom:stop_zoom] + mydataDF['absolute time [s]'].iloc[0], #mydataDF['absolute time [s]'].iloc[start_zoom:stop_zoom],  #correct_time[start_zoom:stop_zoom] - time_offset,
    'rectified signal':rec_signal_ctrl[start_zoom:stop_zoom],
    'Butterworth':butt_signal_ctrl[start_zoom:stop_zoom],
    'RMS':rms_env_ctrl[start_zoom:stop_zoom]
})

start_zoom = 1000
stop_zoom = len(mydataDF.index)
df_interp_ctrl = pd.DataFrame({ 
    'name': 'interpolated my data',
    'time': time_array_ctrl[start_zoom:stop_zoom] + mydataDF['absolute time [s]'].iloc[0],  #correct_time[start_zoom:stop_zoom] - time_offset,
    'rectified signal':abs(ctrl_data_interp[start_zoom:stop_zoom]),
    'Butterworth':butt_signal_interp_ctrl[start_zoom:stop_zoom],
    'RMS':rms_env_interp_ctrl[start_zoom:stop_zoom]
})


df_both = pd.concat([df, df_interp_ctrl])#, df_interp
title_str = os.path.basename(os.path.dirname(os.path.dirname(data_dir))) +' '+ os.path.basename(os.path.dirname(data_dir))

fig = px.line(df_interp_ctrl, x='time', y=['Butterworth'], color='name', title =title_str)

# fig = px.line(df_ctrl, x='time CTRL', y=['rec CTRL', 'RMS CTRL'])
# fig2 = px.line(df, x='time', y=['rectified signal', 'RMS'])

fig.show()
# fig2.show()

# fig, ax = plt.subplots()

## Interpolate to recreate time vector in postprocessing

#assume 1000Hz sampling rate -> 
# end_time =emgDF['relative_time'].iloc[-1] # will be end_abs - start_abs
# sr_freq = 1500
# nb_samples = int(sr_freq*end_time)
# time_array = np.linspace(0, end_time, nb_samples)

# rec_time_array = np.linspace(0, end_time, len(df.index))
# # TODO : use linspac eot approx time instead of recorded time array wiht issues 
# s = interpolate.InterpolatedUnivariateSpline(rec_time_array, df['RMS'])
# interp_emg = s(time_array)

# ax.plot(rms_env)
# ax.plot(rms_env_ctrl[16576:])
# ax.plot(interp_emg)
# ax.set_ylim([-1000, 1000])

plt.show()
