from modules import emg_utils as myfct
from modules.emg_analysis_test_features import Emg_analysis_features



Cecile = Emg_analysis_features(data_dir = r'../emg_recordings/13-01-2023/', 
                               file_calibration = 'calib_cecile/mydata.csv', 
                               file_mydata = 'cecile_task_2/cecile_task_2/mydata.csv', 
                               start_idx = 89, 
                               end_idx = 147,
                               )

Torstein = Emg_analysis_features(data_dir = r'../emg_recordings/12-01-2023/', 
                               file_calibration = 'torstein_calib_half/mydata.csv', 
                               file_mydata = 'torstein_task_2/mydata.csv', 
                               start_idx = 76,
                               end_idx =  124,
                               )

myfct.plot_emgDF(Cecile.normDF)