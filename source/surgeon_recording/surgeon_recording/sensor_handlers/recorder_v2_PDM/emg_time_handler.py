import csv
import json
import os
import sys
import time
from os.path import join

import numpy as np

# ######
#
# Handler to save start and end time of EMG -> NO DATA RECORDING HERE
#
# ######

class EMGTimeHandler:
    def __init__(self, csv_path1):

        # path of csv file to write start and end time
        self.csv_path_emg_time = join(os.path.dirname(csv_path1), "emg_duration.csv") 
        self.start_time = time.time() #in case of early close
    
    def start_emg(self):
        self.start_time = time.time()
        
    def shutdown_emg(self):
        # Save duration in separate file
        end_time = time.time()
        time_to_save = [['Start time', self.start_time, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time))], 
                        ['End time', end_time, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))], 
                        ['Duration', end_time-self.start_time, 'seconds']]
        np.savetxt(self.csv_path_emg_time, time_to_save, delimiter =", ", fmt ='% s')
        print("emg closed cleanly")
     

    
   
def main():
    return
       
    


if __name__ == '__main__':
    main()