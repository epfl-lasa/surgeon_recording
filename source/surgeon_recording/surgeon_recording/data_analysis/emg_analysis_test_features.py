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
data_dir = r'../emg_recordings/12-01-2023/'
path_to_calibration = data_dir + 'torstein_calib_half/mydata.csv'
path_to_mydata = data_dir + 'torstein_task_2/mydata.csv'


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
myfct.plot_emgDF(normDF, title_str='Normalized EMG - Torstein')

#FEATURE EXTRACTION
labels_list = cleanemg_calib.columns.values.tolist() #takes all the names of the columns into a list
window_length = 300
idx_label_studied = 15
label_studied = cleanemg_calib.columns.values.tolist()[idx_label_studied]

#Selecting the 2nd knot
norm2 = normDF[label_studied].iloc[76*SR : 124*SR]
myfct.plot_emgDF(norm2, title_str='Normalized EMG - Torstein')

# Integrated EMG - pre-activation index for muscle activity
