#IMPORTS 
import emg_utils as myfct
import matplotlib.pyplot as plt
import scipy.signal as sp
from scipy.fft import fft
import pyemgpipeline as pep
import EntropyHub as EH
import numpy as np
from matplotlib.figure import SubplotParams
import os 
import pywt
import pandas as pd


#GLOBAL VARIABLES
SR = 1500 #sampling rate
emg_placement = 'Jarque-Bou'


# Path to mydata.csv folder
## Torstein
data_dir = r'../emg_recordings/12-01-2023/'
path_to_calibration = data_dir + 'torstein_calib_half/mydata.csv'
path_to_mydata = data_dir + 'torstein_task_2/mydata.csv'

# ##Cécile
# data_dir = r'../emg_recordings/13-01-2023/'
# path_to_calibration = data_dir + 'calib_cecile/mydata.csv'
# path_to_mydata = data_dir + 'cecile_task_2/cecile_task_2/mydata.csv'


#FILTERING
cleanemg_calib = myfct.clean_emg(path_to_calibration, emg_placement)   
cleanemgDF = myfct.clean_emg(path_to_mydata, emg_placement)   

#Butterworth
butt_calib = myfct.butterworth_filter(cleanemg_calib)
butt = myfct.butterworth_filter(cleanemgDF)

#Interpolation and rectification
interp_calib = myfct.interpolate_clean_emg(butt_calib, start_idx=0)
interp_calib = abs(interp_calib) #rectify 
interpDF = myfct.interpolate_clean_emg(butt, start_idx=50)
interpDF = abs(interpDF) # rectify

#Amplitude normalization
norm_calib = myfct.normalization(interp_calib, interp_calib) #just to verify
normDF = myfct.normalization(interpDF, interp_calib)
# myfct.plot_emgDF(normDF, title_str='Normalized EMG - Cécile')

#FEATURE EXTRACTION
labels_list = cleanemg_calib.columns.values.tolist() #takes all the names of the columns into a list
window_length = 300
idx_label_studied = 15
label_studied = cleanemg_calib.columns.values.tolist()[idx_label_studied]

#Selecting the 2nd knot
start_idx = 89*SR
end_idx = 147*SR
norm2 = normDF.copy()
for label in labels_list[2:]:
    norm2[label] = normDF[label].iloc[start_idx : end_idx]

norm2= norm2.dropna(how="any")
# myfct.plot_emgDF(norm2, title_str='Normalized EMG - Torstein')


#FEATURE EXTRACTION
# Integrated EMG - pre-activation index for muscle activity
iemgDF = pd.DataFrame(columns = labels_list[2:])
for label in labels_list[2:]:
    iemgDF[label] = [abs(norm2[label]).sum()]
    
#Mean absolute value
mavDF = pd.DataFrame(columns = labels_list[2:])
for label in labels_list[2:]:
    mavDF[label] = [(1/window_length)*abs(norm2[label]).sum()]

#Single square integral (SSI) - energy of the EMG signal
ssiDF = pd.DataFrame(columns = labels_list[2:])
for label in labels_list[2:]:
    ssiDF[label] = [(abs(norm2[label])**2).sum()]
    
#Variance - Power of EMG
varDF = pd.DataFrame(columns = labels_list[2:])
for label in labels_list[2:]:
    varDF[label] = [(1/(window_length-1))*(norm2[label]**2).sum()]
    
#Root Mean Square - amplitude modulated Gaussian random process where the RMS is related to the constant force, and the non-fatigue constractions of the muscles
rmsDF = pd.DataFrame(columns = labels_list[2:])
for label in labels_list[2:]:
    rmsDF[label] = [((norm2[label]**2).mean()) **0.5]
    
#Waveform Length - cumulative length of the waveform over the segment
wlDF = pd.DataFrame(columns = labels_list[2:])
for label in labels_list[2:]:
    wlDF[label]= [abs(norm2[label].diff()).sum()]
    
#Power spectrum density of the normalized dataframe
psdDF = pd.DataFrame(columns=labels_list[2:])
f = pd.DataFrame(columns=labels_list[2:])
RMSamplitude = []
for label in labels_list[2:]:
    f[label], psdDF[label] = sp.periodogram(norm2[label], SR, 'flattop', scaling='spectrum')

    # The peak height in the power spectrum is an estimate of the RMS amplitude.
    RMSamplitude.append(np.sqrt(psdDF[label].max()))

#Frequency median - the frequency where the power spectrum is divided into two equal parts
fmdDF =  pd.DataFrame(columns=labels_list[2:])
for label in labels_list[2:]:
    fmdDF[label] = [(psdDF[label].sum())*0.5]
    
#Frequency mean - average of the frequency
fmnDF = pd.DataFrame(columns=labels_list[2:])
for label in labels_list[2:]:
    fmnDF[label] = [(psdDF[label]*f[label]).sum() / psdDF[label].sum()]