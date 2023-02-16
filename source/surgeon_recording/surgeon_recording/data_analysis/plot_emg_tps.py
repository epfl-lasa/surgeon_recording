from emg_utils import *
from tps_utils import * 

data_dir = '/home/maxime/Workspace/surgeon_recording/exp_data/13022023/1/1/'
path_to_tps = data_dir + 'TPS_calibrated.csv'
path_to_mydata = data_dir + 'emg/task/mydata.csv'

emg_placement = 'Protocol'

# plot_tps_csv(path_to_tps)

cleantpsDF = clean_tps(path_to_tps)   
print(f"Recording duration : {cleantpsDF['relative time'].iloc[-1]:.2f} s" )
plot_tpsDF(cleantpsDF, title_str='Calibrated TPS', time_for_plot='absolute time', nb_rec_channels=6)

# get starting time of TPS
# WARNING : abs time in emg is in seconds, abs time in tps is in ms -> NEED TO FIX in recorder
start_time = get_starting_time(cleantpsDF)

cleanemgDF = clean_emg(path_to_mydata, emg_placement)   
# plot_emgDF(cleanemgDF)
print(f"Recording duration : {cleanemgDF['relative time'].iloc[-1]:.2f} s" )
plot_emgDF(cleanemgDF, title_str='Interpolated EMG', time_for_plot='absolute time', nb_rec_channels=4, plot_from_time=start_time)