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


# TODO (?) : put functions in an object for easier import, can put data_path and some variables as properties in init
  
# Path to mydata.csv folder
data_dir = os.path.join(os.getcwd(), 'source/surgeon_recording/surgeon_recording', 'emg_recordings/12-01-2023/') #r'../emg_recordings/12-01-2023/'
path_to_calibration = data_dir + 'torstein_calib_half/mydata.csv'
path_to_mydata = data_dir + 'torstein_task_2/mydata.csv'

emg_placement = 'Jarque-Bou'
  
# myfct.plot_mydata_raw(path_to_mydata)
# myfct.plot_mydata_raw(path_to_calibration)

cleanemg_calib = myfct.clean_emg(path_to_calibration, emg_placement)   
cleanemgDF = myfct.clean_emg(path_to_mydata, emg_placement)   
# myfct.plot_emgDF(cleanemg_calib)
#myfct.plot_emgDF(cleanemgDF)
print(f"Calibration recording duration : {cleanemg_calib['relative time'].iloc[-1]:.2f} s")
print(f"Recording duration : {cleanemgDF['relative time'].iloc[-1]:.2f} s")


# # CHOOSE CUT OFF FREQ 
# ch1=cleanemgDF["Flexor Carpi Ulnaris R"].to_numpy()
# ch1 = myfct.interpolate_clean_emg(cleanemgDF)
# ch1_fft = fft(ch1)
# # ch1_fft_db = plt.magnitude_spectrum(ch1_fft, scale = "dB")
# ch1_fft_db = plt.magnitude_spectrum(ch1_fft)

# time = mydataDF['absolute time [s]'].to_numpy()
# N = len(ch1)
# n = np.arange(N)
# sr=1500
# T = N/sr
# freq = n/T

# # plt.plot(1/np.array(time), ch1_fft_db[0])
# plt.plot(freq, np.abs(ch1_fft_db[0]))

# # plt.xscale("log")
# plt.show()
# # Obtained freq at -3dB is 8*10^-6 Hz which is really small ...


# TODO : check the effect of butt, interp and rms on the signal


butt_calib = myfct.butterworth_filter(cleanemg_calib)
butt = myfct.butterworth_filter(cleanemgDF)
# myfct.plot_emgDF(butt_calib)
# myfct.plot_emgDF(butt)

interp_calib = myfct.interpolate_clean_emg(butt_calib, start_idx=0)
interp_calib = abs(interp_calib) #rectify 
interpDF = myfct.interpolate_clean_emg(butt, start_idx=50)
interpDF = abs(interpDF) # rectify
# myfct.plot_emgDF(interpDF, title_str='Interpolated EMG')
# myfct.plot_emgDF(interp_calib, title_str='Interpolated calibrated EMG')


rms_calib = myfct.rms_filter(interp_calib)


# AMPLITUDE NORMALIZATION
# for col in range (2, rms_calib.shape[1]):
    # max_col = rms_calib.iloc[:, col].nlargest(7) #finds the 7 highest values of each column
    # min_col = rms_calib.iloc[:, col].nsmallest(7) #finds the  smallest values of each column
    # mean_max_col = max_col.mean() #mean of the highest values
    # mean_min_col = min_col.mean()
    # L_mean_max.append(mean_max_col)
    # L_mean_min.append(mean_min_col)
    # normDF_calib.iloc[:,col] = (normDF_calib.iloc[:,col] - mean_min_col) / (mean_max_col - mean_min_col)
    # normDF.iloc[:,col] = (normDF.iloc[:,col] - mean_min_col) / (mean_max_col - mean_min_col)
    
norm_calib = myfct.normalization(interp_calib, interp_calib)
normDF = myfct.normalization(interpDF, interp_calib)


# PLOT EFFECT OF PRE FILTERS 
label_studied = cleanemg_calib.columns.values.tolist()[15]
# plt.plot(cleanemg_calib["relative time"], cleanemg_calib[label_studied], color= 'b', label = "cleanemg_calib", alpha = 0.5)
#plt.plot(butt_calib["relative time"], butt_calib[label_studied], color= 'r', label = "butt_calib", alpha = 0.5)
# plt.plot(interp_calib["relative time"], interp_calib[label_studied], color= 'c', label = "interp_calib", alpha = 0.5)
# plt.plot(rms_calib["relative time"], rms_calib[label_studied], color= 'g', label = "rms_calib", alpha = 0.5)
# plt.plot(norm_calib["relative time"], norm_calib[label_studied], label='Normalized calibration EMG')


# plt.legend()
# plt.xlim([0, 600])
# plt.show()

# FEATURE EXTRACTION
labels_list = cleanemg_calib.columns.values.tolist()

# -LINEAR ENVELOPE: creates lowpass filter and apply to rectified signal to get EMG envelope
low_pass = 8/(SR/2) #8Hz is the Fc
b2, a2 = sp.butter(4, low_pass, btype='lowpass')
envelopeDF = normDF.copy()
for label in labels_list[2:]:
    envelopeDF[label] = sp.filtfilt(b2, a2, normDF[label].values)
    
# -RMS
rmsDF = myfct.rms_filter(normDF)

# -POWER SPECTRUM
N = normDF.shape[0]
T = N/SR
n = np.arange(N)
freq = n/T

f, Pxx_spec = sp.periodogram(normDF, SR, 'flattop', scaling='spectrum')

# The peak height in the power spectrum is an estimate of the RMS amplitude.
RMSamplitude = np.sqrt(Pxx_spec.max())

#-GAUSSIAN MOVING WINDOW
# gaussDF = normDF.copy() #gaussian smoothing on normDF
gaussDF = envelopeDF.copy() #gaussian smoothing on normDF
for label in labels_list[2:]:
    gaussDF[label] = gaussDF[label].rolling(window = 450, win_type='gaussian', center=True).sum(std=1)

#-HAMMING MOVING WINDOW
hammDF = normDF.copy()
for label in labels_list[2:]:
    hammDF[label] = hammDF[label].rolling(window = 5, win_type='hamming', center=True).sum()


#-PYEMGPIPELINE
# mgr = pep.wrappers.DataProcessingManager()
# emg_plot_params = pep.plots.EMGPlotParams(
#     n_rows=16,
#     n_cols=1,
#     fig_kwargs={
#         'figsize': (16, 4),
#         'subplotpars': SubplotParams(top=0.8, wspace=0.1, hspace=0.4)})
# mgr.set_data_and_params(normDF.values.tolist(), hz=SR, channel_names=labels_list, emg_plot_params=emg_plot_params)

# c = mgr.process_all(is_plot_processing_chain=True, is_overlapping_trials=True,
#                     cycled_colors=['brown', 'green'],
#                     legend_kwargs={'loc':'right', 'bbox_to_anchor':(1.4, 0.5), 'fontsize':'small'},
#                     axes_pos_adjust=(0, 0, 0.75, 1))


# PLOT FILTERS fOR FEATURE EXTRACTION 
# plt.plot(normDF["relative time"], normDF[label_studied], color= 'b', label = "normDF", alpha = 0.5)
plt.plot(envelopeDF["relative time"], envelopeDF[label_studied], color= 'b', label = "envelopeDF", alpha = 0.5)
# plt.plot(rmsDF["relative time"], rmsDF[label_studied], color= 'g', label = "rmsDF", alpha = 0.5)
plt.plot(gaussDF["relative time"], gaussDF[label_studied], color= 'r', label = "gaussDF", alpha = 0.5)
# plt.plot(hammDF["relative time"], hammDF[label_studied], color= 'r', label = "hammDF", alpha = 0.5)


# plt.semill('ogy(freq, np.sqrt(normDF[label_studied]), color= 'r', label = "rmsDF")
# plt.xlabel('frequency [Hz]')
# plt.ylabeLinear spectrum [V RMS]')


plt.legend()
plt.xlim([0, cleanemgDF['relative time'].iloc[-1]])
plt.show()

# myfct.plot_emgDF(envelopeDF, title_str='EnvelopeDF EMG')
# myfct.plot_emgDF(rmsDF, title_str='rmsDF EMG')


#myfct.plot_emgDF(rmsDF,title_str = "Cécile rms_calib_3 21.12.22", ytitle = 'EMG of calibration [mV]')


  

