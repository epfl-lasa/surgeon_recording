import numpy as np
import zmq
import time
import sys
from surgeon_recording.sensor_handler import SensorHandler

# # deifne the directory of the emgAcquireClient python_module 
# emgAcquire_dir = r"C:\Users\buschbapti\Documents\GitHub\surgeon_recording\source\emgAcquire\python_module"
# #emgAcquire_dir = "/home/buschbapti/Documents/Zeiss/surgeon_recording/source/emgAcquire/python_module"

# # append the path including the directory of the python_module
# sys.path.append(emgAcquire_dir)
# # import the module
# import emgAcquireClient

class EMGHandler(SensorHandler):
    def __init__(self, nb_channels, emg_ip="localhost", streaming_ip="127.0.0.1", port=5558):
        SensorHandler.__init__(self, 'emg', timestep=0.01, header=['emg' + str(i) for i in range(nb_channels)], ip=streaming_ip, port=port)
        # define number of channels to acquire
        self.nb_channels = nb_channels
        # create an emgClient object for acquiring the data
        #self.emgClient = emgAcquireClient.emgAcquireClient(svrIP=emg_ip, nb_channels=self.nb_channels)
        # initialize the node
        #init_value = self.emgClient.initialize()

        init_value = -1

        self.emg_init = init_value == 0

        self.emg_data = []
        
        if self.emg_init:
            self.emgClient.start()

    def acquire_data(self):
        # acquire the signals from the buffer
        # emg_array = self.emgClient.getSignals()
        emg_array = self.generate_fake_data([self.nb_channels, 50])

        returned_data = []
        with self.lock:
            # append the array with the new data
            if self.emg_data:
                prev_time = self.emg_data[-1][1]
                index = self.emg_data[-1][0]
            else:
                prev_time = self.start_time
                index = 0
            last_sample_time = time.time()
            dt = (last_sample_time - prev_time)/len(emg_array[0])
            for i in range(len(emg_array[0])):
                data = [index + 1]
                t = prev_time + (i+1) * dt
                data.append(t)
                # keep the updating period
                data.append(t - self.start_time)
                data = data + emg_array[:, i].tolist()
                index = data[0]
                returned_data.append(data)
        self.emg_data = returned_data
        return returned_data

    def setup_recording(self, recording_folder, start_time):
        super().setup_recording(recording_folder, start_time)
        with self.lock:
            self.emg_data = [] 

    def shutdown(self):
        super().shutdown()
        if self.emg_init:
            self.emgClient.shutdown()


def main(args=None):
    emg_handler = EMGHandler(9)
    emg_handler.run()
    
if __name__ == '__main__':
    main()