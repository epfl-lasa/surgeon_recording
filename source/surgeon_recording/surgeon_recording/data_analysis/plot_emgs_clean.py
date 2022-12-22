from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import csv
import numpy as np
import scipy.signal as sp
import matplotlib.pyplot as plt
import os
from scipy import interpolate

data_dir = r'C:/Users/LASA/Documents/Recordings/surgeon_recording/test_data/20-12-2022/calibration_torstein_1/'
path_to_mydata = data_dir + 'mydata.csv'

# Choose emg channel 
# TODO : make it so we have all channels automatically
channel = 'ch1'

mydataDF = pd.read_csv(path_to_mydata, sep=';', header=0) #, usecols=['time [ms]', 'absolute time [s]', channel])

# Clip EMG values
# mydataDF[channel].clip(-8000, 8000, inplace=True)

# Convert time array ( ms to s)
correct_time = mydataDF['time [ms]'] * 1e-3

# Interpolate Data to deal wit potntial packet loss
#modif by cecile

start_idx = 500 # remove bad data at start of recording 
start_time = mydataDF['absolute time [s]'].iloc[start_idx]
end_time =  mydataDF['absolute time [s]'].iloc[-1] #mydataDF['time [ms]'].iloc[-1] * 1e-3 # will be end_abs - start_abs
duration = end_time - start_time

# print("Compare durations : ", duration, end_time-mydataDF['absolute time [s]'].iloc[0], mydataDF['time [ms]'].iloc[-1] * 1e-3 )

sr_freq = 1500
nb_samples = int(sr_freq*duration)
time_array_ctrl = np.linspace(0, duration, nb_samples)

rec_time_array = np.linspace(0, duration, len(mydataDF.index[start_idx:]))
# rec_time_array = correct_time[start_idx:]
s = interpolate.InterpolatedUnivariateSpline(np.array(rec_time_array), mydataDF[channel].iloc[start_idx:])
ctrl_data_interp = s(time_array_ctrl)

# Print to chekc interpolated signal should have more points than original
print("SHAPES :", np.shape(mydataDF[channel]), np.shape(ctrl_data_interp))

# Filter EMG
# Butterworth filter
# TODO : make as a function 
fs = 1500 #approximate sampling frequency for emg
fny = fs/2 #nyquist frequency
fco = 25  #cut off frequency
rms_window = 20 #window size for rms
N = 4

[b, a] = sp.butter(N, 1.16*fco/fny)
butt_signal_interp_ctrl = sp.filtfilt(b, a, abs(ctrl_data_interp))

# RMS
rms_env_interp_ctrl = np.sqrt(np.convolve(np.square(abs(ctrl_data_interp)), np.ones(rms_window)/rms_window, mode='same'))

# DF for plot
# Use 'zoom' to plot less than complete signal
start_zoom = 1000
stop_zoom = len(mydataDF.index)
df_interp_ctrl = pd.DataFrame({ 
    'name': 'interpolated mydata',
    'time': time_array_ctrl[start_zoom:stop_zoom] + mydataDF['absolute time [s]'].iloc[0],  #correct_time[start_zoom:stop_zoom] - time_offset,
    'rectified signal':abs(ctrl_data_interp[start_zoom:stop_zoom]),
    'Butterworth':butt_signal_interp_ctrl[start_zoom:stop_zoom],
    'RMS':rms_env_interp_ctrl[start_zoom:stop_zoom]
})

# Title string
title_str = os.path.basename(os.path.dirname(os.path.dirname(data_dir))) +' '+ os.path.basename(os.path.dirname(data_dir) + " " + channel)

# Line to plot
# TODO : change y to plot different filters ( can be a list of strings ['rectified signal', 'RMS'])
fig = px.line(df_interp_ctrl, x='time', y=['Butterworth'], color='name', title =title_str)
fig.show()

# Plot raw emg signal 
nb_channels = 8

fig = make_subplots(rows=nb_channels, cols=1, shared_xaxes=True, vertical_spacing=0.02,
subplot_titles=mydataDF.columns.values.tolist()[2:])

for ch_nbr in range(1, nb_channels+1):

    fig.add_trace(go.Scatter(x=mydataDF['time [ms]'], y=mydataDF['ch'+str(ch_nbr)]), row=ch_nbr, col=1)


