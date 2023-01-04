import emg_utils as myfct

# TODO (?) : put functions in an object for easier import, can put data_path and some variables as properties in init
  
# Path to mydata.csv folder
data_dir = r'C:/Users/cabasse/Documents/Microsurgery/test_cecile/calibration_cecile/'
#path_to_mydata = data_dir + 'mydata.csv'
path_to_mydata = data_dir + 'mydata_light.csv'
emg_placement = 'Protocol'
  
#myfct.plot_mydata_raw(path_to_mydata)

cleanemgDF = myfct.clean_emg(path_to_mydata, emg_placement)   
#myfct.plot_emgDF(cleanemgDF)
print(f"Recording duration : {cleanemgDF['relative time'].iloc[-1]:.2f} s" )

# Might not be necessary for data analysis
interpDF = myfct.interpolate_clean_emg(cleanemgDF, start_idx=50)
#myfct.plot_emgDF(interpDF, title_str='Interpolated EMG')
butt = myfct.butterworth_filter(interpDF)
# myfct.plot_emgDF(butt)
  
rms = myfct.rms_filter(cleanemgDF)
# myfct.plot_emgDF(rms)