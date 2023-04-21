from modules.emg_utils import *
from modules.tps_utils import * 

data_dir = 'exp_data/170423/1/1/'
path_to_tps = data_dir + 'TPS_calibrated.csv'
path_to_emg = data_dir + 'emg_data_task.csv'
path_to_emg_calib = data_dir + 'emg_data_calibration.csv'

emg_placement = 'Jarque-Bou'

# plot_tps_csv(path_to_tps)

plt.close('all')

cleantpsDF = clean_tps(path_to_tps)

# Filter outliers
cleantpsDF = remove_outlier_hampel(cleantpsDF, labels_to_filter=['Left Thumb'])
# plot_tpsDF(cleantpsDF, title_str='Calibrated TPS', time_for_plot='relative time', nb_rec_channels=6, show_plot=False)   
print(f"Recording duration : {cleantpsDF['relative time'].iloc[-1]:.2f} s" )

# Remove bias
measure_bias_start = 550 # seconds
measure_bias_end = 600 # seconds
unbiasedDF = remove_bias(cleantpsDF, time_to_measure_bias=[560,600], show_values=True)
# plot_tpsDF(unbiasedDF2, title_str=f'BIAS from {measure_bias_start}s to {measure_bias_end}s TPS', time_for_plot='relative time', nb_rec_channels=6, show_plot=False)

# DEBUG prints

# highest_values_idx = cleantpsDF.idxmax(axis=0)[2:]
# highest_values_time = cleantpsDF['relative time'].iloc[highest_values_idx.values]
# print("Highest value : ", cleantpsDF.max(axis=0)[2:])
# print("Higest Values time : \n", highest_values_time)

# lowest_values = unbiasedDF.min(axis=0)[2:]
# lowest_values_idx = unbiasedDF.idxmin(axis=0)[2:]
# lowest_values_time = unbiasedDF['relative time'].iloc[lowest_values_idx.values]
# print("Lowest Values : \n", lowest_values)
# print("Lowest Values time : \n", lowest_values_time)

# plt.show()

# get starting time of TPS
# WARNING : abs time in emg is in seconds, abs time in tps is in ms -> NEED TO FIX in recorder
# start_time = get_starting_time(cleantpsDF)

cleanemgDF = clean_emg(path_to_emg, emg_placement)  
emgcalibDF = clean_emg(path_to_emg_calib, emg_placement) 

normemgDF = normalization(cleanemgDF, emgcalibDF)
# plot_emgDF(cleanemgDF)
# print(f"Recording duration : {cleanemgDF['relative time'].iloc[-1]:.2f} s" )
# plot_emgDF(cleanemgDF, title_str='Interpolated EMG', time_for_plot='absolute time', nb_rec_channels=16, plot_from_time=start_time)

# PLOTS BOTH TOGETHER 
time_range = [40, 440] # seconds
labels_for_emg = ['Extensor Digitorum L',
        'Flexor Digitorum Superficialis L',
        'Abductor Pollicis longus and extensor pollicis brevis L',
        'Abductor Pollicis Brevis L']

labels_for_tps = ['Left Index', 'Left Thumb']

plot_tps_emg(unbiasedDF, normemgDF, labels_for_tps, labels_for_emg, time_range)