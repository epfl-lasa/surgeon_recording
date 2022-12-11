import plotly.express as px
import pandas as pd
import csv
import numpy as np
import scipy.signal as sp
import matplotlib.pyplot as plt
from scipy import interpolate

data_dir = r'C:/Users/LASA/Documents/Recordings/surgeon_recording/test_data/09-12-2022/test_4/'
path_to_mydata = data_dir + 'mydata.csv'
path_to_emg = data_dir + 'emg.csv'

mydataDF = pd.read_csv(path_to_mydata, sep=';', header=0, usecols=['time', 'ch1'])
emgDF = pd.read_csv(path_to_emg, usecols=['relative_time', 'emg0', 'index_buffer'])

# CHANGE THIS VALUE FOR EACH DATASET (time diffesrence between mydata and emg recordings - FOR PLOT)
time_offset = 2.16
# test 1 09 - 18.587729
# test 2 09 - 3.677729
# test 1 07 - 10.67141
# test 4 07 - 4.47602 #
# test2 07 - 10.78141 
# test1 02 - 3.72224 # seconds

#print(emgDF.head())

# Check time array 
# end_time = emgDF['time'].iloc[-1]
# print(end_time)
# lin_time = np.linspace(0, end_time, len(emgDF.index))
# time_df = pd.DataFrame({'csv_time': emgDF['time'], 'lin_time': lin_time})
# print(time_df.head())
# fig = px.line(time_df)

# Interpolate data to deal with packet loss
end_time =emgDF['index_buffer'].iloc[-1] # will be end_abs - start_abs
print(end_time)
sr_freq = 1000
nb_samples = int(sr_freq*end_time)
time_array = np.linspace(0, end_time, nb_samples)

rec_time_array = np.linspace(0, end_time, len(emgDF['relative_time'].iloc[:-1]))
s = interpolate.InterpolatedUnivariateSpline(rec_time_array, emgDF['emg0'].iloc[:-1])
data_interp = s(time_array)
print("SHAPES :", np.shape(emgDF['emg0']), np.shape(data_interp))

# interp control
end_time = mydataDF['time'].iloc[-1] * 1e-3 # will be end_abs - start_abs
sr_freq = 1500
nb_samples = int(sr_freq*end_time)
time_array_ctrl = np.linspace(0, end_time, nb_samples)

rec_time_array = np.linspace(0, end_time, len(mydataDF.index))
s = interpolate.InterpolatedUnivariateSpline(rec_time_array, mydataDF['ch1'])
ctrl_data_interp = s(time_array_ctrl)
print("SHAPES :", np.shape(mydataDF['ch1']), np.shape(ctrl_data_interp))


print("number fo samples vs estimated:", len(emgDF.index), nb_samples)

# Convert time array ( ms to s)
correct_time = mydataDF['time'] * 1e-3

# Filter current - EMG
data_current = emgDF['emg0'].iloc[:-1]
data_current_control = mydataDF['ch1']

# fig, ax1 = plt.subplots()

# ax1.plot(data_current_control)
# ax1.plot(ctrl_data_interp)


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
butt_signal_interp = sp.filtfilt(b, a, abs(data_interp))

# take enveloppe using rms windowing
rms_env = np.sqrt(np.convolve(np.square(rec_signal), np.ones(rms_window)/rms_window, mode='same'))
rms_env_ctrl = np.sqrt(np.convolve(np.square(rec_signal_ctrl), np.ones(rms_window)/rms_window, mode='same'))

# Interpolate rms only
rms_interp = np.sqrt(np.convolve(np.square(abs(data_interp)), np.ones(rms_window)/rms_window, mode='same'))


# s = interpolate.InterpolatedUnivariateSpline(rec_time_array, rms_env)
# rms_interp = s(time_array)

#PLOT to compare enveloppes, zoom on 1 part
start_zoom = 0
stop_zoom = len(emgDF.index)-10#1000

df = pd.DataFrame({
    'name': 'emg recorder',
    'time': emgDF['relative_time'].iloc[start_zoom:stop_zoom],
    'rectified signal':rec_signal[start_zoom:stop_zoom],
    'Butterworth':butt_signal[start_zoom:stop_zoom],
    'RMS':rms_env[start_zoom:stop_zoom] #rms_env[start_zoom:stop_zoom]
})

start_zoom = 10
stop_zoom = len(time_array)-10#1000

df_interp = pd.DataFrame({
    'name': 'Interpolated emg recorder',
    'time': time_array[start_zoom:stop_zoom],
    'rectified signal': abs(data_interp[start_zoom:stop_zoom]),
    'Butterworth':butt_signal_interp[start_zoom:stop_zoom],
    'RMS':rms_interp[start_zoom:stop_zoom] #rms_env[start_zoom:stop_zoom]
})

start_zoom = 0
stop_zoom = len(mydataDF.index)
df_ctrl = pd.DataFrame({ 
    'name': 'my data',
    'time': correct_time[start_zoom:stop_zoom] - time_offset,
    'rectified signal':rec_signal_ctrl[start_zoom:stop_zoom],
    'Butterworth':butt_signal_ctrl[start_zoom:stop_zoom],
    'RMS':rms_env_ctrl[start_zoom:stop_zoom]
})

df_both = pd.concat([df, df_ctrl, df_interp])
fig = px.line(df_both, x='time', y=['Butterworth'], color='name')

# fig = px.line(df_ctrl, x='time CTRL', y=['rec CTRL', 'RMS CTRL'])
# fig2 = px.line(df, x='time', y=['rectified signal', 'RMS'])

fig.show()
# fig2.show()

# fig, ax = plt.subplots()

## Interpolate to recreate time vector in postprocessing

#assume 1000Hz sampling rate -> 
end_time =emgDF['relative_time'].iloc[-1] # will be end_abs - start_abs
sr_freq = 1500
nb_samples = int(sr_freq*end_time)
time_array = np.linspace(0, end_time, nb_samples)

rec_time_array = np.linspace(0, end_time, len(df.index))
# TODO : use linspac eot approx time instead of recorded time array wiht issues 
s = interpolate.InterpolatedUnivariateSpline(rec_time_array, df['RMS'])
interp_emg = s(time_array)

# ax.plot(rms_env)
# ax.plot(rms_env_ctrl[16576:])
# ax.plot(interp_emg)
# ax.set_ylim([-1000, 1000])

plt.show()
