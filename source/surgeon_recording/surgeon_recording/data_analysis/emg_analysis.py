# IMPORTS
import modules.emg_utils as myfct
import matplotlib.pyplot as plt
import scipy.signal as sp
import pyemgpipeline as pep
from scipy.fft import fft
import EntropyHub as EH
import numpy as np
#import antropy as ant
from matplotlib.figure import SubplotParams
import os 
import pywt
import pandas as pd

# GLOBAL VAR 
SR = 1500
emg_placement = 'Jarque-Bou'

# TODO (?) : put functions in an object for easier import, can put data_path and some variables as properties in init
  
# Path to mydata.csv folder
data_dir = r'../emg_recordings/17-04-2023/'
path_to_calibration = data_dir + 'emg_data_calibration.csv'
path_to_mydata = data_dir + 'emg_data_task.csv'

  
# myfct.plot_mydata_raw(path_to_mydata)
# myfct.plot_mydata_raw(path_to_calibration)

cleanemg_calib = myfct.clean_emg(path_to_calibration, emg_placement)   
cleanemgDF = myfct.clean_emg(path_to_mydata, emg_placement)   
# myfct.plot_emgDF(cleanemg_calib)
#myfct.plot_emgDF(cleanemgDF)
print(f"Calibration recording duration : {cleanemg_calib['relative time'].iloc[-1]:.2f} s")
print(f"Recording duration : {cleanemgDF['relative time'].iloc[-1]:.2f} s")

## CONVERT THE MUSCLES LABELS INTO A LIST
labels_list = cleanemg_calib.columns.values.tolist()
idx_label_studied = 15
label_studied = cleanemg_calib.columns.values.tolist()[idx_label_studied]


## SEE FOURIER TRANSFORM OF CLEAN DATA TO VERIFY REAL SAMPLING RATE
diff_cleanemg_calib = cleanemg_calib["relative time"].diff() #to see what is the sampling rate
diff_cleanemg_calib = diff_cleanemg_calib[400:] #remove points
freq_cleanemg_calib = 1/diff_cleanemg_calib
print("the maximum frequency is in Hz : ", max(freq_cleanemg_calib))
print("the mean frequency is in Hz : ", freq_cleanemg_calib.mean())
#plt.plot(freq_cleanemg_calib)

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
    
# norm_calib = myfct.normalization(interp_calib, interp_calib) #just to verify
normDF = myfct.normalization(interpDF, interp_calib)
# myfct.plot_emgDF(normDF, title_str='Normalized EMG - Cécile',nb_rec_channels=16)

# PLOT EFFECT OF PRE FILTERS 
# plt.plot(cleanemg_calib["relative time"], cleanemg_calib[label_studied], color= 'b', label = "cleanemg_calib", alpha = 0.5)
#plt.plot(butt_calib["relative time"], butt_calib[label_studied], color= 'r', label = "butt_calib", alpha = 0.5)
# plt.plot(interp_calib["relative time"], interp_calib[label_studied], color= 'c', label = "interp_calib", alpha = 0.5)
# plt.plot(rms_calib["relative time"], rms_calib[label_studied], color= 'g', label = "rms_calib", alpha = 0.5)
# plt.plot(norm_calib["relative time"], norm_calib[label_studied], label='Normalized calibration EMG')


# plt.legend()
# plt.xlim([0, 600])
# plt.show()

# FEATURE EXTRACTION
# -LINEAR ENVELOPE: creates lowpass filter and apply to rectified signal to get EMG envelope
low_pass = 8/(SR/2) #8Hz is the Fc
b2, a2 = sp.butter(4, low_pass, btype='lowpass')
envelopeDF = normDF.copy()
for label in labels_list[2:]:
    envelopeDF[label] = sp.filtfilt(b2, a2, normDF[label].values)

#-GAUSSIAN MOVING WINDOW ON LINEAR ENVELOPE
gaussDF = envelopeDF.copy() #gaussian smoothing on envelopeDF
for label in labels_list[2:]:
    gaussDF[label] = gaussDF[label].rolling(window = 380, win_type='gaussian', center=True).sum(std=1)
    
#-HAMMING MOVING WINDOW ON LINEAR ENVELOPE
hammDF = envelopeDF.copy()
for label in labels_list[2:]:
    hammDF[label] = hammDF[label].rolling(window = 5, win_type='hamming', center=True).sum()
    
    
# -RMS
rmsDF = myfct.rms_filter(normDF)

# -POWER SPECTRUM
psdDF = pd.DataFrame(columns=labels_list)
f = pd.DataFrame(columns=labels_list)
RMSamplitude = []
for label in labels_list[2:]:
    f[label], psdDF[label] = sp.periodogram(normDF[label], SR, 'flattop', scaling='spectrum')

    # The peak height in the power spectrum is an estimate of the RMS amplitude.
    RMSamplitude.append(np.sqrt(psdDF[label].max()))

print('Peak height of power spectrum = ' + str(round(RMSamplitude[idx_label_studied], 4)) + ' Hz')


# -FREQUENCY MEAN - average of the frequency
fmnDF = psdDF.copy()

for label in labels_list[2:]:
    fmnDF[label] = (psdDF[label]*f[label]).rolling(window = 300).sum() / psdDF[label].rolling(window = 300).sum()
  
fmnDF = fmnDF.dropna(how='all')
    



#-DAUBECHIES WAVELET TRANSFORM
w1 = myfct.lowpassfilter(normDF[label_studied], thresh = 0.05, wavelet="db1")
w2 = myfct.lowpassfilter(normDF[label_studied], thresh = 0.05, wavelet="db2")
w4 = myfct.lowpassfilter(normDF[label_studied], thresh = 0.05, wavelet="db4")
w6 = myfct.lowpassfilter(normDF[label_studied], thresh = 0.05, wavelet="db6")
w20 = myfct.lowpassfilter(normDF[label_studied], thresh = 0.05, wavelet="db20")

fig, axs = plt.subplots(5, 1, sharex='col')

#TODO : Verify why normDF[label_studied].shape = 550277 and w1.shape = 550278
axs[0].plot(normDF["relative time"], normDF[label_studied], normDF["relative time"], w1[:-1], label='db4' )
axs[1].plot(normDF["relative time"], normDF[label_studied], normDF["relative time"], w2[:-1], label='db2' )
axs[2].plot(normDF["relative time"], normDF[label_studied], normDF["relative time"], w4[:-1], label='db4' )
axs[3].plot(normDF["relative time"], normDF[label_studied], normDF["relative time"], w6[:-1], label='db6' )
axs[4].plot(normDF["relative time"], normDF[label_studied], normDF["relative time"], w20[:-1], label='db20' )

axs[0].set_ylabel('normDF and db1 (mV)')
axs[1].set_ylabel('normDF and db2 (mV)')
axs[2].set_ylabel('normDF and db4 (mV)')
axs[3].set_ylabel('normDF and db6 (mV)')
axs[4].set_ylabel('normDF and db20 (mV)')

# fig.tight_layout()
# plt.subplots_adjust(top=0.95,
#                     bottom=0.04,
#                     left=0.055,
#                     right=0.995,
#                     hspace=0.4,
#                     wspace=0.2)
# plt.xlim([0, normDF['relative time'].iloc[-1]])
# axs.legend()
# axs.set_title('Removing High Frequency Noise with DWT', fontsize=18)
# axs[4].set_xlabel('Time')
# plt.show()
# # Best = bd4



# #-SAMPLE ENTROPY -NOT WORKING YET, MIGHT NOT BE USEFUL, ADD A ROLING WINDOW 
# SampEnDF = []
# for label in labels_list[2:]:
#     std = np.std(cleanemgDF[label])
#     SampEnDF.append( ant.sample_entropy(cleanemgDF[label].to_numpy(), order = int(0.2 * std)))
 
#-IEMG                   
iemgDF = normDF.copy()
for label in labels_list[2:]:
    iemgDF[label] = iemgDF[label].rolling(window=300).sum()



# PLOT FILTERS fOR FEATURE EXTRACTION 
# plt.plot(cleanemgDF["relative time"], cleanemgDF[label_studied], color= 'b', label = "cleanemgDF", alpha = 0.5)
# plt.plot(normDF["relative time"], normDF[label_studied], color= 'b', label = "normDF", alpha = 0.5)

# plt.plot(envelopeDF["relative time"], envelopeDF[label_studied], color= 'b', label = "envelopeDF", alpha = 0.5)
# plt.plot(rmsDF["relative time"], rmsDF[label_studied], color= 'g', label = "rmsDF", alpha = 0.5)
# plt.plot(gaussDF["relative time"], gaussDF[label_studied], color= 'r', label = "gaussDF", alpha = 0.5)
# plt.plot(hammDF["relative time"], hammDF[label_studied], color= 'r', label = "hammDF", alpha = 0.5)
# plt.plot(SampEnDF["relative time"], SampEnDF[label_studied], color= 'r', label = "SampEnDF", alpha = 0.5)


# print('Peak height of power spectrum = ' + str(round(RMSamplitude[idx_label_studied], 4)) + ' Hz')

# plt.semilogy(f[label_studied], np.sqrt(Pxx_spec[label_studied]), color= 'r', label = "Power spectrum DF")
# plt.xlabel('frequency [Hz]')
# plt.ylabel('Linear spectrum [V RMS]')


# plt.legend()
# plt.xlim([0, cleanemgDF['relative time'].iloc[-1]])
# plt.show()

# myfct.plot_emgDF(envelopeDF, title_str='EnvelopeDF EMG')
# myfct.plot_emgDF(rmsDF, title_str='rmsDF EMG')


#myfct.plot_emgDF(rmsDF,title_str = "Cécile rms_calib_3 21.12.22", ytitle = 'EMG of calibration [mV]')


  

