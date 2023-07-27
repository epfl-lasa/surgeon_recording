import sys 
import os

current_directory = os.path.dirname(os.path.abspath(__file__) )
subfolder_path = os.path.join(current_directory, 'modules')
sys.path.append(subfolder_path)

from emg_utils import *
from tps_utils import * 

data_dir = 'E:/Surgeon_Skill_Assessment/Data_Cluj_June_2023/S_37_120623/TSK_1/TRL_1/'
# path_to_tps = data_dir + 'TPS_calibrated.csv'
path_to_mydata = data_dir + 'emg_data_task.csv'
path_to_mydata_calib = data_dir + 'emg_data_calibration.csv'


emg_placement = 'Protocol'

# plot_tps_csv(path_to_tps)

plt.close('all')

# cleantpsDF = clean_tps(path_to_tps)
# plot_tpsDF(cleantpsDF, title_str='Calibrated TPS', time_for_plot='relative time', nb_rec_channels=6, show_plot=False)   
# print(f"Recording duration : {cleantpsDF['relative time'].iloc[-1]:.2f} s" )

## Use bias from start
# unbiasedDF = remove_bias(cleantpsDF, time_to_measure_bias=[20,120])
# plot_tpsDF(unbiasedDF, title_str='BIAS from START TPS', time_for_plot='relative time', nb_rec_channels=6, show_plot=False)

# # Use bias from end
# unbiasedDF2 = remove_bias(cleantpsDF, time_to_measure_bias=[530,560], show_values=True)
# plot_tpsDF(unbiasedDF2, title_str='BIAS from END TPS', time_for_plot='relative time', nb_rec_channels=6, show_plot=False)

# lowest_values = unbiasedDF2.min(axis=0)[2:]
# lowest_values_idx = unbiasedDF2.idxmin(axis=0)[2:]
# lowest_values_time = unbiasedDF2['relative time'].iloc[lowest_values_idx.values]
# print("Lowest Values : \n", lowest_values)
# print("Lowest Values time : \n", lowest_values_time)

# plt.show()

# get starting time of TPS
# WARNING : abs time in emg is in seconds, abs time in tps is in ms -> NEED TO FIX in recorder
# start_time = get_starting_time(cleantpsDF)

cleanemgDF = clean_emg(path_to_mydata, emg_placement, nb_rec_channels=15)   
plot_emgDF(cleanemgDF[100:3000000])

cleanemgDF_calib = clean_emg(path_to_mydata_calib, emg_placement, nb_rec_channels=15)
plot_emgDF(cleanemgDF_calib[100:1000000])

# print(f"Recording duration : {cleanemgDF['relative time'].iloc[-1]:.2f} s" )
# plot_emgDF(cleanemgDF, title_str='Interpolated EMG', time_for_plot='absolute time', nb_rec_channels=16, plot_from_time=start_time)