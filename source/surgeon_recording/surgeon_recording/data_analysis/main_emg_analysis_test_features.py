import emg_utils as myfct
from emg_analysis_test_features import Emg_analysis_features


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

#Selecting the 2nd knot
##Torstein 
start_idx = 76*SR
end_idx = 124*SR

# ##Cécile
# start_idx = 89*SR
# end_idx = 147*SR