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

        self.time_vect1 = [time.time()]
        self.time_start = time.time()
      
        
    def shutdown_emg(self):
        # Save duration in separate file
        end_time = time.time()
        time_to_save = [['Start time', self.time_start], ['End time', end_time], ['Duration', end_time-self.time_start]]
        np.savetxt(self.csv_path_emg_time, time_to_save, delimiter =", ", fmt ='% s')

        self.emgClient.shutdown()
        self.emg_file.close()
        print("emg closed cleanly")
     

    
   
def main():
    return
       
    


if __name__ == '__main__':
    main()