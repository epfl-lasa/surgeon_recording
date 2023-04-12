# IMPORTS
import emg_utils as myfct
import matplotlib.pyplot as plt
import scipy.signal as sp
import pyemgpipeline as pep
import numpy as np
from matplotlib.figure import SubplotParams
import os 

# GLOBAL VAR 
SR = 1500
emg_placement = 'Jarque-Bou'

# Path to mydata.csv folder
data_dir = os.path.join(os.getcwd(), 'source/surgeon_recording/surgeon_recording', 'emg_recordings/12-01-2023/') #r'../emg_recordings/12-01-2023/'
path_to_calibration = data_dir + 'torstein_calib_half/mydata.csv'
path_to_mydata = data_dir + 'torstein_task_2/mydata.csv'


#-PEMGPIPELINE

# Data reformatting to correspond wiht library (remove time array)
all_timestamp = []
all_data = []

# Get raw data, remove last line to avoid size error( due to missing values in last row)
data = np.genfromtxt(path_to_mydata, delimiter=';', skip_header=5, skip_footer=5, usecols=(2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17), missing_values='Nan', filling_values = 0)

print(data.shape)
#Remove rows woth Nan
data = data[~np.isnan(data).any(axis=1)]

# Check if the NumPy array contains any NaN value
if(np.isnan(data).any()):
    print("The Array contain NaN values")
else:
    print("The Array does not contain NaN values")


# initialize EMGMeasurement
m = pep.wrappers.EMGMeasurement(data, hz=SR)

# apply seven processing steps
m.apply_dc_offset_remover()
m.apply_bandpass_filter(bf_order=4, bf_cutoff_fq_lo=5, bf_cutoff_fq_hi=420)
m.apply_full_wave_rectifier()
m.apply_linear_envelope(le_order=4, le_cutoff_fq=8)
m.apply_end_frame_cutter(n_end_frames=2)
# m.apply_amplitude_normalizer(max_amplitude=1.5)
# m.apply_segmenter(beg_ts=0.01, end_ts=0.04)

# plot final result
m.plot()




  

