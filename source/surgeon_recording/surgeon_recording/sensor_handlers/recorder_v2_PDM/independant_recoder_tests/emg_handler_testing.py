import csv
import json
import os
import sys
import time
from os.path import join
import keyboard

import numpy as np
import pandas as pd

# define the directory of the emgAcquireClient python_module 
emgAcquire_dir = r"C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emgAcquire/python_module"
# append the path including the directory of the python_module
sys.path.append(emgAcquire_dir)
# import the module
import emgAcquireClient


class EMGHandler_new:
    def __init__(self, csv_path1, csv_path2):

        # path of csv file to write data
        self.csv_path_emg1 = csv_path1
        
        # to count the number of time we access the buffer
        self.count = 0

        # Testing variables
        self.loop_dur_csv = csv_path2
        self.full_loop_duration = []
        self.writing_time = []
        self.acquire_time = []
        self.global_idx = []
        self.buffer_idx = []
        self.abs_time = []
        self.rel_time = []
        self.buffer_data = []

        self.parameters_emg=[]
        self.get_parameters_emg()

        #force status to on
        self.running_emg = (self.parameters_emg['status'] == 'on')


        if self.running_emg:
            # define number of channels to acquire
            self.nb_channels = self.parameters_emg["nb_channels"]
        
            # create an emgClient object for acquiring the data
            self.emgClient = emgAcquireClient.emgAcquireClient(freq=20, nb_channels = self.nb_channels)
            # initialize the node
            init_test = self.emgClient.initialize()
            if init_test<0:
                print("unable to initialize")
                exit()
            self.emgClient.start()
            self.time_start = time.time()
            
            self.emg_data = []
            
            # set up csv file
            self.emg_file = open(self.csv_path_emg1, 'w', newline='')
            self.writer_emg = csv.writer(self.emg_file)
            header_emg = ["index_global", "index_buffer", "absolute_time", "relative_time"] + self.parameters_emg["header"]
            self.writer_emg.writerow(header_emg)

            self.time_vect1 = [time.time()]
            


    # get the parameters (nb of channels status) from the file
    def read_config_file(self, sensor_name):
        filepath = os.path.abspath(os.path.dirname(__file__))
        with open(join(filepath, '..','..','..','..', 'config', 'sensor_parameters.json'), 'r') as paramfile:
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
        
        # test loop duration
        start_time = time.time()

        # get data from buffer
        acq_start_time = time.time()

        emg_data = self.emgClient.getSignals()

        acq_duration = time.time()-acq_start_time

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


        writing_start_time = time.time()

        # write data: global index (total), index in the buffer (from 0 to 50), absolute time, relative time, data for teh channels
        for index in range(len(emg_data[1])):
            row = [len(emg_data[1])*self.count + index_data[index], index, tmp_time_vector[index], tmp_time_vector[index]-self.time_start]
            for c in range(self.nb_channels):
                row.append(emg_data[c][index])
            self.writer_emg.writerow(row)

        write_duration = time.time() - writing_start_time
        loop_duration = time.time() - start_time

        # Check for why 0 duration loops occur at freq >= 20
        if loop_duration == 0:
            print("0 loop")
            print("Size buffer:", size_buffer)

        # Save loop duration
        self.full_loop_duration.append(loop_duration)
        self.writing_time.append(write_duration)
        self.acquire_time.append(acq_duration)

        # WORTHLESS - CANT REORD MORE THAN 10seconds without OOM at the end when trying to saveq
        # self.global_idx.extend([len(emg_data[1])*self.count + idx for idx in index_data])
        # self.buffer_idx.extend(index_data)
        # self.abs_time.extend(tmp_time_vector)
        # self.rel_time.extend([tmp_time_vec - self.time_start for tmp_time_vec in tmp_time_vector])
        # self.buffer_data.extend(emg_data.T) #TODO : hstack might work better ?? (exten dmight reorder data wrong)

        # DEBUG PRINT
        if self.count % 10 == 0  :
            print("Acq message size:", np.shape(emg_data))

        # count the number of times we got the data from the buffer
        self.count = self.count + 1
    
        
    def shutdown_emg(self):
        end_time = time.time()

        time_dict = {"full loop duration": self.full_loop_duration,
                    "acquire duration" : self.acquire_time,
                    "writing duration": self.writing_time}

        time_df = pd.DataFrame(time_dict)
        time_df.to_csv(self.loop_dur_csv)

        # Save all to dict then csv
        # TODO: separate each channel for further data proc (or do that later maybe?)
        data_dict = {'index_global': self.global_idx, 
                    'index_buffer': self.buffer_idx,
                    'absolute_time': self.abs_time,
                    'relative_time': self.rel_time,
                    'emg_channels': self.buffer_data}
        
        data_df = pd.DataFrame.from_dict(data=data_dict)
        # data_df.to_csv(r"/Users/LASA/Documents/Recordings/surgeon_recording/test_data/07-12-2022/emg_df.csv")
        # np.savetxt(r"/Users/LASA/Documents/Recordings/surgeon_recording/test_data/07-12-2022/emg_data_only.csv", self.buffer_data)
        print("saved data all good")

        print("Count =", self.count)

        # Add recording duration at end of file
        row = ["Recording Duration [s]",end_time-self.time_start ]
        row.extend(np.zeros(2+self.nb_channels)) # to avoid Nan issues
        self.writer_emg.writerow(row)

        self.emgClient.shutdown()
        self.emg_file.close()
        print("emg closed cleanly")
     

   
def main():

    is_looping_emg = True
    print("Start Time:", time.time())

    data_dir = r"/Users/LASA/Documents/Recordings/surgeon_recording/test_data/09-12-2022/"
    csv_path = data_dir + "emg.csv"

    loop_dur_path = data_dir + "loop_durations.csv"

    handler_emg = EMGHandler_new(csv_path, loop_dur_path)
    start_end_time = []
    start_end_time.append(time.time())

    while is_looping_emg is True:
        handler_emg.acquire_data_emg()
        
        if keyboard.is_pressed('q'):
            start_end_time.append(time.time())
            print("Recording Duration : ", start_end_time[1]-start_end_time[0])
            print('goodbye emg')
            
            handler_emg.shutdown_emg()
            is_looping_emg = False
    
    return
       
    


if __name__ == '__main__':
    main()