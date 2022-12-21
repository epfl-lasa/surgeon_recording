import csv
import json
import os
import sys
import time
from os.path import join

import numpy as np

# define the directory of the emgAcquireClient python_module 
emgAcquire_dir = r"C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emgAcquire/python_module"

# append the path including the directory of the python_module
sys.path.append(emgAcquire_dir)
# import the module
import emgAcquireClient

class EMGHandler_new:
    def __init__(self, csv_path1):

        # path of csv file to write data
        self.csv_path_emg1 = csv_path1

        # path of csv file to write start and end time
        self.csv_path_emg_time = join(os.path.dirname(csv_path1), "emg_duration.csv")
        
        # to count the number of time we access the buffer
        self.count = 0

        self.parameters_emg=[]
        self.get_parameters_emg()

        #force status to on
        self.running_emg = (self.parameters_emg['status'] == 'on')


        if self.running_emg:
            # define number of channels to acquire
            self.nb_channels = self.parameters_emg["nb_channels"]
        
            # create an emgClient object for acquiring the data
            self.emgClient = emgAcquireClient.emgAcquireClient(nb_channels = self.nb_channels)
            # initialize the node
            init_test = self.emgClient.initialize()
            if init_test<0:
                print("unable to initialize")
                exit()

            # set up csv file
            self.emg_file = open(self.csv_path_emg1, 'w', newline='')
            self.writer_emg = csv.writer(self.emg_file)
            header_emg = ["index_global", "index_buffer", "absolute_time", "relative_time"] + self.parameters_emg["header"]
            self.writer_emg.writerow(header_emg)

            self.emg_data = []

            self.emgClient.start()

            self.time_vect1 = [time.time()]
            self.time_start = time.time()


    # get the parameters (nb of channels status) from the file
    def read_config_file(self, sensor_name):
        filepath = os.path.abspath(os.path.dirname(__file__))
        with open(join(filepath, '..','..','..', 'config', 'sensor_parameters.json'), 'r') as paramfile:
            config = json.load(paramfile)
        if not sensor_name in config.keys():
            config[sensor_name] = {}
            config[sensor_name]['status'] = 'off'
        return config[sensor_name]
     

    def get_parameters_emg(self):
        self.parameters_emg = self.read_config_file('emg')
        if self.parameters_emg['status'] != 'off':
           self.parameters_emg.update({ 'header': ['emg' + str(i) for i in range(self.parameters_emg['nb_channels'])]})
        return self.parameters_emg


    def acquire_data_emg(self):
        
        ## test with time condition to access the buffer only when it is full 
        ## tried different amount of time but not better results
        #while (time.perf_counter()-time_vect1[-1]) < 0.048:
        #pass
        
        # Test with time perf counter: should be more precise BUT The reference point of the returned value is undefined, so that only the difference between the results of consecutive calls is valid. 
        # when emg only; reference was approx 0 because luck but with all sensors ref might start when we run the script = not good
        
        #if self.count == 0:
            #self.start_time = time.perf_counter()
            #print(self.start_time)
            #self.time_vect1 = [0]
            #time_abs = (time.time())
        
        # get data from buffer
        emg_data = self.emgClient.getSignals()

        #self.time_vect1.append(time.perf_counter()-self.start_time)
        
        # take the absolute time of the computer when receiving the buffer (50 data)
        self.time_vect1.append(time.time())
        
        # keep the last 2 timestamps in memory
        if len(self.time_vect1) > 2:
            self.time_vect1 = [self.time_vect1[-2], self.time_vect1[-1]]
        
        # index of data in the buffer (from 0 to lenght of data)
        index_data = list(range(len(emg_data[1])))

        # get the amount of data points we got
        size_buffer = len(emg_data[1])

        # interpolate the time for each data points (assuming equal dt for all points in the buffer)
        dt = (self.time_vect1[-1]-self.time_vect1[-2])/size_buffer
        tmp_time_vector = np.linspace(self.time_vect1[-2], self.time_vect1[-2]+(dt*size_buffer),size_buffer,endpoint=False)

        
        # write data: global index (total), index in the buffer (from 0 to 50), absolute time, relative time, data for teh channels
        for index in range(len(emg_data[1])):
            row = [len(emg_data[1])*self.count + index_data[index], index, tmp_time_vector[index], tmp_time_vector[index]-self.time_start]
            for c in range(self.nb_channels):
                row.append(emg_data[c][index])
            self.writer_emg.writerow(row)

        # count the number of times we got the data from the buffer
        self.count = self.count + 1
    
        
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