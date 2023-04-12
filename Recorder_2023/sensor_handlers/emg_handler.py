import time
import numpy as np
import subprocess
import json
import os
import autopy

# ######
#
# Handler to save start and end emgAcquire cpp code + record time and start and end
#
# ######

class EMGHandler:
    def __init__(self, csv_path):

        # path of csv file to write start and end time
        self.csv_path_emg_time = csv_path
        self.start_time = time.time() #in case of early close

        self.emgAcq_cwd = "/Users/LASA/Documents/Recordings/surgeon_recording/Recorder_2023/emgAcquire/"
        self.path_to_exe = "/Users/LASA/Documents/Recordings/surgeon_recording/Recorder_2023/emgAcquire/build/emgAcquire.exe"
        self.config_file = "config.json"
    
    def start_emg(self):
        self.start_time = time.time()

        self.emgAcq_process = subprocess.Popen([self.path_to_exe, self.config_file], cwd=self.emgAcq_cwd)

        # Wait for software to open
        time.sleep(0.5)

        # Move mouse and click on EMG window
        autopy.mouse.move(1100, 664)
        autopy.mouse.click()
    
    def write_config_file(self, folder_name, subject, task, emg_file_label):
        # args are path for data file
        # emg_label to name csv file correctly

        # Set path to config file
        config_file_path = os.path.join(self.emgAcq_cwd, "cfg", self.config_file)

        # Read config file
        with open(config_file_path, 'r') as f :
            config = json.load(f)
            print(os.path.join("..","..","exp_data",folder_name,subject,task,"emg_data_"+emg_file_label))
            config["saveFile"] = os.path.join("..","..","exp_data",folder_name,subject,task,"emg_data_"+emg_file_label)

        # Remove old config file
        os.remove(config_file_path)

        # rewrite new config file 
        with open(config_file_path, 'w')as f :
            json.dump(config, f, indent=4)

    def update_start_time(self):
        self.start_time = time.time()

    def shutdown_emg(self):
        # Save duration in separate file
        self.emgAcq_process.terminate()
        end_time = time.time()
        time_to_save = [['Start time', self.start_time, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time))], 
                        ['End time', end_time, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))], 
                        ['Duration', end_time-self.start_time, 'seconds']]
        np.savetxt(self.csv_path_emg_time, time_to_save, delimiter =", ", fmt ='% s')
        print("EMG closed cleanly. \n")
     