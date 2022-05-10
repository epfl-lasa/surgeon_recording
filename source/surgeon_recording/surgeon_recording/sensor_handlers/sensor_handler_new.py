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


class Recorder():
    def __init__(self):

        self.parameters_emg=[]
        self.parameters_optitrack=[]

        self.get_parameters_emg()
        self.get_parameters_optitrack()

        self.running_optitrack = (self.parameters_optitrack['status'] == 'on')
        self.running_emg = (self.parameters_emg['status'] == 'on')
        
        if self.running_optitrack:
            self.handler_opti = OptitrackHandlerNew()

            self.header_optitrack = self.parameters_optitrack['header']
            self.data_optitrack = []
            
            #self.index_optitrack = 0
            
            #self.stop_event = Event()
            self.recording_thread_opti = Thread(target=self.optitrack_thread)
            self.recording_thread_opti.start()
            self.lock = Lock()

            self.received_frames = {}

            for frame in self.parameters_optitrack['frames']:
                label = frame['label']
                self.received_frames[frame['streaming_id']] = {'label': label, 'position': [], 'orientation': [], 'timestamp': 0}

            

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
            self.recording_thread_emg.start()


    def read_config_file(sensor_name):
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
            self.parameters_emg.update({ 'header': ['emg' + str(i) for i in range(self.parameters['nb_channels'])]})
        return self.parameters_emg
    
    def get_parameters_optitrack(self):
        self.parameters_optitrack = self.read_config_file('optitrack')
        if self.parameters_optitrack['status'] != 'off' and self.parameters_optitrack['status'] != 'remote':
            header = []
            for frame in self.parameters_optitrack['frames']:
                label = frame['label']
                header = header + [label + '_x', label + '_y', label + '_z', label + '_qx', label + '_qy', label + '_qz', label + '_qw']
            self.parameters_optitrack.update({ 'header': header })
        return self.parameters_optitrack

  

  
    def optitrack_thread(self):
        start_time_opti = time.time()
        while self.running_optitrack:
            self.row_optitrack = start_time_opti
            self.writer_opti.writerow(self.row_optitrack) 
            # automatique donc pas besoin de acquire, slmt besoin de lancer le process ?

    def emg_thread(self):
        
    count = 0
    count_all =0
    time_vect1 = [0]
    freq_vect1 = []
    freq_vect2 = []

    time_vect2 = [0]


    start_time = time.perf_counter()
    time_vect1 = [start_time]

        while self.running_emg:
            emg_data = emgClient.getSignals()
            time_vect1.append(time.perf_counter())
   
            time_vect2.append(time.time())
    
            if count > 0:
            freq_vect1.append(1/(time_vect1[-1]-time_vect1[-2]))
            #freq_vect2.append(1/(time_vect2[-1]-time_vect2[-2]))

            all_Data = np.hstack((all_Data, emg_data))
    
            index_data = list(range(len(emg_data[1])))
            dt = (time_vect1[-1]-time_vect1[-2])/50
            tmp_time_vector = np.linspace(time_vect1[-2], time_vect1[-2]+(dt*50),50,endpoint=False)
    
            for index in range(len(emg_data[1])):
                row = [len(emg_data[1])*count + index_data[index], index, tmp_time_vector[index]]
                for c in range(nb_ch):
                    row.append(emg_data[c][index])
            writer.writerow(row)
            count = count + 1
   

    if time.perf_counter() - start_time > duration:
        print("stoping")
        
        is_looping = False
        f.close()



    def shutdown_thread(self):

        is_looping = False
            handler.opt_client.shutdown()
            handler.f.close()


    def main(args=None):
        recorder = Recorder()
        recorder.optitrack_thread()
    
if __name__ == '__main__':
    main()