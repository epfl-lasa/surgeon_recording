from importlib.abc import ResourceReader
import numpy as np
import zmq
import csv
from threading import Thread, Event, Lock
import os
from os.path import join
import time
import json

from surgeon_recording.sensor_handlers.optitrack_handler_new import OptitrackHandlerNew


class RecorderNew():
    def __init__(self):

        self.lock = ()
        self.csv_path_optitrack = "/Users/LASA/Documents/Recordings/surgeon_recording/data/new_recorder/optitrack_1.csv"


        """self.parameters_emg=[]
    
        self.get_parameters_emg()
        
        self.running_emg = (self.parameters_emg['status'] == 'on')
        
    

        if self.running_emg:
            self.header_emg = self.parameters_emg['header']
            #ip_emg = self.parameters_emg['streaming_ip']
            #port_emg = self.parameters_emg['streaming_port']
            self.nb_channels = self.parameters_emg["nb_channels"]

            # create an emgClient object for acquiring the data
            self.emgClient = emgAcquireClient.emgAcquireClient(svrIP=parameters["sensor_ip"], nb_channels=self.nb_channels)
            # initialize the node
            init_value = self.emgClient.initialize()
            self.emg_init = init_value == 0
            self.emgClient.start()
            
            self.data_emg = []
            
            #self.stop_event = Event()
            self.recording_thread_emg = Thread(target=self.emg_thread)
            self.recording_thread_emg.start()"""


    """def read_config_file(sensor_name):
        filepath = os.path.abspath(os.path.dirname(__file__))
        with open(join(filepath, '..', '..', 'config', 'sensor_parameters.json'), 'r') as paramfile:
            config = json.load(paramfile)
        if not sensor_name in config.keys():
            config[sensor_name] = {}
            config[sensor_name]['status'] = 'off'
        return config[sensor_name]"""
    
    """def get_parameters_emg(self):
        self.parameters_emg = self.read_config_file('emg')
        if self.parameters_emg['status'] != 'off':
            self.parameters_emg.update({ 'header': ['emg' + str(i) for i in range(self.parameters['nb_channels'])]})
        return self.parameters_emg"""
    

    def start_threads(self):

        #self.stop_event = Event()
        recording_thread_opti = Thread(target=self.optitrack_thread)
        recording_thread_opti.start()
        self.lock = Lock()


    def optitrack_thread(self):
        is_looping = True
        start_time_loop = time.time()
        handler_opti = OptitrackHandlerNew(self.csv_path_optitrack)

        while is_looping:
            handler_opti.write_optitrack_data()
            if time.time() - start_time_loop > 10:
                is_looping = False
                handler_opti.shutdown_optitrack()

    
    """def emg_thread(self): 
    """

    """def shutdown_thread(self):
        is_looping = False
            handler.opt_client.shutdown()
            handler.f.close()"""


def main():
    recorder = RecorderNew()
    recorder.start_threads()
    
if __name__ == '__main__':
    main()