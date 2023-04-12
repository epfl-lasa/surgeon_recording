from os.path import join
from sensor_handlers.tps_calib import TPScalibration

# File to output the calibrated tps data from the raw recording 

folder_input = "13022023"
subject_input = "1"
task_input = "1"
folder = join("/Users/LASA/Documents/Recordings/surgeon_recording/exp_data", folder_input, subject_input, task_input)


       
csv_path_tps_raw = join(folder, "TPS_recording_raw.csv")
csv_path_tps_cal = join(folder, "TPS_calibrated.csv")



calib_tps = TPScalibration(folder_path = folder, csv_path = csv_path_tps_cal, folder_input = folder_input, subject_nb=subject_input, csv_raw_data=csv_path_tps_raw)

