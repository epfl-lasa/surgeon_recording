import emg_utils as myfct

# TODO (?) : put functions in an object for easier import, can put data_path and some variables as properties in init
  
# Path to mydata.csv folder
data_dir = r'../emg_recordings/21-12-2022/'
path_to_calibration = data_dir + 'calib_3/mydata.csv'
path_to_mydata = data_dir + 'task_1/mydata.csv'

emg_placement = 'Jarque-Bou'
  
#myfct.plot_mydata_raw(path_to_mydata)
#myfct.plot_mydata_raw(path_to_calibration)

cleanemg_calib = myfct.clean_emg(path_to_calibration, emg_placement)   
# cleanemgDF = myfct.clean_emg(path_to_mydata, emg_placement)   
# myfct.plot_emgDF(cleanemg_calib)
#myfct.plot_emgDF(cleanemgDF)
print(f"Calibration recording duration : {cleanemg_calib['relative time'].iloc[-1]:.2f} s")
# print(f"Recording duration : {cleanemgDF['relative time'].iloc[-1]:.2f} s")


# # CHOOSE CUT OFF FREQ 
# mydataDF = pd.read_csv(path_to_mydata, sep=';', header=0)
# mydataDF = mydataDF.loc[:,~mydataDF.columns.str.match("Unnamed")]

# ch1 = mydataDF["ch1"].to_numpy()
# ch1_fft = fft(ch1)
# ch1_fft_db = plt.magnitude_spectrum(ch1_fft, scale = "dB")

# time = mydataDF['absolute time [s]'].to_numpy()

# plt.plot(1/np.array(time), ch1_fft_db[0])
# plt.xscale("log")
# plt.show()
# # Obtained freq at -3dB is 8*10^-6 Hz which is really small ...



# Might not be necessary for data analysis
butt_calib = myfct.butterworth_filter(cleanemg_calib)
# butt = myfct.butterworth_filter(interpDF)
# myfct.plot_emgDF(butt_calib)
# myfct.plot_emgDF(butt)

# TODO : Look into interpolate_clean_emg
#interp_calib = myfct.interpolate_clean_emg(butt_calib, start_idx=0)
# interpDF = myfct.interpolate_clean_emg(cleanemgDF, start_idx=50)
#myfct.plot_emgDF(interpDF, title_str='Interpolated EMG')
#myfct.plot_emgDF(interp_calib, title_str='Interpolated calibrated EMG')

rms_calib = myfct.rms_filter(butt_calib)
# rms = myfct.rms_filter(cleanemgDF)
#myfct.plot_emgDF(rms_calib.iloc[:910000,:],title_str = "Cécile rms_calib_3 21.12.22", ytitle = 'EMG of calibration [mV]')
#myfct.plot_emgDF(rms)


# AMPLITUDE NORMALIZATION
#normDF = rms
normDF_calib = rms_calib

#to compare the different calibrations
L_mean_max =[]
L_mean_min = []
L_max = []

for col in range (2, rms_calib.shape[1]):
    max_col = rms_calib.iloc[1000:, col].nlargest(7) #finds the 7 highest values of each column
    i_max_col = max_col.index
    
    min_col = rms_calib.iloc[:, col].nsmallest(7) #finds the  smallest values of each column
    i_min_col = min_col.index
    
    mean_max_col = max_col.mean() #mean of the highest values
    mean_min_col = min_col.mean()
    
    L_max.append(i_max_col.max()) #list of max value for each column ie each muscle
   
    
    L_mean_max.append(mean_max_col)
    L_mean_min.append(mean_min_col)
    # max_col = rms_calib.iloc[:, col].max() #finds the highest value of each column
    # min_col = rms_calib.iloc[:, col].min() #finds the smallest value of each column
  
    normDF_calib.iloc[:,col] = (normDF_calib.iloc[:,col] - min_col) / (max_col - min_col)

    # normDF.iloc[:,col] = (normDF.iloc[:,col] - min_col) / (max_col - min_col)
  #  normDF.iloc[:,col] = (normDF.iloc[:,col] - mean_min_col) / (mean_max_col - mean_min_col)
  


# myfct.plot_emgDF(normDF)
#myfct.plot_emgDF(normDF.iloc[:910000,:],title_str = "Torstein calib_1 20.12.22") #910000 is the max I could plot
myfct.plot_emgDF(normDF_calib)

expected = [0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]
c1 = [12, 0, 1, 2, 8, 4, 7, 10, 5, 6, 3, 13, 14, 9, 11, 15] #calib1
c2= [0, 14, 10, 8, 1, 3, 2, 15, 13, 11, 7, 9, 6, 5, 4, 12] #calib2
c3 = [0, 1, 11, 13, 9, 14, 2, 3, 7, 12, 6, 15, 10, 5, 8, 4] #calib3

print("[nb of common pts compared to expected, the common emgs channels]", myfct.calibration_validation(L_max))
