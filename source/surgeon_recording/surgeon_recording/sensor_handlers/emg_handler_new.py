import numpy as np
import time
import sys
import os
from os.path import join
import csv
import json




# deifne the directory of the emgAcquireClient python_module 
#emgAcquire_dir = r"C:\Users\LASA\Documents\Recordings\surgeon_recording\source\emgAcquire\python_module"
emgAcquire_dir = r"C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emgAcquire/python_module"

# append the path including the directory of the python_module
sys.path.append(emgAcquire_dir)
# import the module
import emgAcquireClient

class EMGHandler_new:
    def __init__(self, csv_path1):

        self.csv_path_emg1 = csv_path1
        start_time = time.perf_counter()

        self.time_vect1 = [start_time]
        self.time_vect2 = [time.time()]

        self.count = 0


        self.parameters_emg=[]
        self.get_parameters_emg()
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
            self.emgClient.start()

            self.emg_data = []
            self.emg_data2 = []
        
            #self.emg_array = []
        
            #self.returned_data = []

            #self.emgClient.run()
            
            self.emg_file = open(self.csv_path_emg1, 'w', newline='')
            self.writer_emg = csv.writer(self.emg_file)
            header_emg = ["index_global", "index_buffer", "absolute_time", "relative_time"] + self.parameters_emg["header"]
            self.writer_emg.writerow(header_emg)


    def read_config_file(self, sensor_name):
        filepath = os.path.abspath(os.path.dirname(__file__))
        with open(join(filepath, '..', '..', 'config', 'sensor_parameters.json'), 'r') as paramfile:
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
        #print("hello")
        #while (time.perf_counter()-time_vect1[-1]) < 0.048:
        #pass
        emg_data = self.emgClient.getSignals()
        self.time_vect1.append(time.perf_counter())
        time_abs = (time.time())

        if len(self.time_vect1) > 2:
            self.time_vect1 = [self.time_vect1[-2], self.time_vect1[-1]]
        
          
        #all_Data = np.hstack((all_Data, emg_data))
        
        index_data = list(range(len(emg_data[1])))

        size_buffer = len(emg_data[1])

        dt = (self.time_vect1[-1]-self.time_vect1[-2])/size_buffer
        tmp_time_vector = np.linspace(self.time_vect1[-2], self.time_vect1[-2]+(dt*size_buffer),size_buffer,endpoint=False)
        
        for index in range(len(emg_data[1])):
     
            row = [len(emg_data[1])*self.count + index_data[index], index, tmp_time_vector[index] + time_abs, tmp_time_vector[index]]
            for c in range(self.nb_channels):
                row.append(emg_data[c][index])
            self.writer_emg.writerow(row)
        self.count = self.count + 1
    
        
    def shutdown_emg(self):
        self.emgClient.shutdown()
        self.emg_file.close()
        print("emg closed cleanly")
        #print(all_Data.shape)
        #print(count)

    
   
def main():
    return
       
    


if __name__ == '__main__':
    main()