import time
from NatNetClient import NatNetClient
import csv
import numpy as np
import os
from os.path import join
import json



class OptitrackHandlerNew:
    def __init__(self, csv_path):
        self.csv_path_optitrack = csv_path
        self.data_dict = []
        self.index_optitrack = []
        self.rel_time = []

        self.count = 0

        self.parameters_optitrack=[]
        self.get_parameters_optitrack()
        self.running_optitrack = (self.parameters_optitrack['status'] == 'on')

        if self.running_optitrack:
            self.header_optitrack = ["index", "relative_time", "absolute time"]
            for i in range(len(self.parameters_optitrack['header'])):
                self.header_optitrack.append(self.parameters_optitrack['header'][i])
            self.data_optitrack = []
        
            self.received_frames = {}

            for frame in self.parameters_optitrack['frames']:
                label = frame['label']
                self.received_frames[frame['streaming_id']] = {'label': label, 'position': [], 'orientation': [], 'timestamp': [], 'timestamp2': [], 'frame_number': [],'received_data1': [],'received_data2': []}



            self.opt_client = NatNetClient()
            self.opt_client.set_print_level(0)

            self.opti = open(self.csv_path_optitrack, 'w', newline='')
            self.writer_opti = csv.writer(self.opti)

            self.writer_opti.writerow(self.header_optitrack)
            self.row_optitrack = []


            # Configure the streaming client to call our rigid body handler on the emulator to send data out.
            self.opt_client.new_frame_listener = self.receive_new_frame
            self.opt_client.rigid_body_listener = self.receive_rigid_body_frame
            # Start up the streaming client now that the callbacks are set up.
            # This will run perpetually, and operate on a separate thread.
            self.opt_client.run()
            self.start_time_opti = time.time()
            self.writer_opti.writerow([self.start_time_opti])

    def read_config_file(self, sensor_name):
        filepath = os.path.abspath(os.path.dirname(__file__))
        with open(join(filepath, '..', '..', 'config', 'sensor_parameters.json'), 'r') as paramfile:
            config = json.load(paramfile)
        if not sensor_name in config.keys():
            config[sensor_name] = {}
            config[sensor_name]['status'] = 'off'
        return config[sensor_name]
     

    def get_parameters_optitrack(self):
        self.parameters_optitrack = self.read_config_file('optitrack')
        if self.parameters_optitrack['status'] != 'off' and self.parameters_optitrack['status'] != 'remote':
            header = []
            for frame in self.parameters_optitrack['frames']:
                label = frame['label']
                header = header + [label + '_x', label + '_y', label + '_z', label + '_qx', label + '_qy', label + '_qz', label + '_qw']
            self.parameters_optitrack.update({ 'header': header })
        return self.parameters_optitrack


    # This is a callback function that gets connected to the NatNet client and called once per mocap frame.
    def receive_new_frame(self, data_dict):
        # order_list = ["frame_number", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
        #               "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "is_recording", "trackedModelsChanged"]
        #if id in self.received_frames.keys():
            self.received_frames[16]['timestamp2'] = data_dict["timestamp"]
            self.received_frames[16]['frame_number'].append(data_dict["frame_number"])
            self.received_frames[16]['received_data1'] = True
            #print("new frame")

            



    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body_frame(self, id, position, rotation):      
        if id in self.received_frames.keys():
            self.received_frames[id]['timestamp'] = time.time()
            self.received_frames[id]['position'] = position
            self.received_frames[id]['orientation'] = rotation
            #print("hello")
            self.received_frames[id]['received_data2'] = True

        
    def write_optitrack_data(self):
        #print("write called")
        """
        tmp = False
        print(self.received_frames[16]['received_data1'])
        if self.received_frames[16]['received_data1'] is True:
            #print("true1")
            self.index_optitrack.append(self.received_frames[16]["frame_number"][-1] - self.received_frames[16]["frame_number"][0])
            self.row_optitrack.append(self.index_optitrack[-1])
            self.row_optitrack.append(self.received_frames[16]["timestamp2"])
            self.row_optitrack.append(self.received_frames[16]["timestamp"])

            for id in self.received_frames.keys():
                if self.received_frames[id]['received_data2'] is True:
                    #print("TRUE")
                    for i in range(len(self.received_frames[id]['position'])):
                        self.row_optitrack.append(self.received_frames[id]['position'][i])
                    for j in range(len(self.received_frames[id]['orientation'])):
                        self.row_optitrack.append(self.received_frames[id]['orientation'][j])
                    self.received_frames[id]['received_data2'] = False
                    tmp = True
                else:
                    print("ZERO")
                    self.row_optitrack.append("0")

            #if len(self.index_optitrack) > 1 and tmp is True and not self.index_optitrack[-1] == self.index_optitrack[-2]: #ecrit a partir du moment ou on a 1 toool
                #flat_row = [item for sublist in self.row_optitrack for item in sublist]
                #print(self.row_optitrack)
                #self.writer_opti.writerow(self.row_optitrack) 
            
            #if len(self.index_optitrack) > 1 and not self.index_optitrack[-1] == self.index_optitrack[-2]: 
            self.received_frames[16]['received_data1'] = False
        else:
            self.row_optitrack.append("0")
        print(self.row_optitrack)
        self.writer_opti.writerow(self.row_optitrack) 
        """        
        
        self.rel_time.append(self.received_frames[16]["timestamp2"])
        self.row_optitrack.append(self.received_frames[16]["timestamp2"])
        self.row_optitrack.append(self.received_frames[16]["timestamp"])
        if len(self.received_frames[16]["frame_number"])> 1:
            self.row_optitrack.append(self.received_frames[16]["frame_number"][-1]-self.received_frames[16]["frame_number"][0])

        """for id in self.received_frames.keys():
            #if self.received_frames[id]['received_data2'] is True:
                #print("TRUE")
            for i in range(len(self.received_frames[id]['position'])):
                self.row_optitrack.append(self.received_frames[id]['position'][i])
            for j in range(len(self.received_frames[id]['orientation'])):
                self.row_optitrack.append(self.received_frames[id]['orientation'][j])
            self.received_frames[id]['received_data2'] = False
            tmp = True"""
    
        #if len(self.rel_time) > 1 and not self.rel_time[-1] == self.rel_time[-2]:
        self.writer_opti.writerow(self.row_optitrack) 
        self.row_optitrack= [] 
        self.count = self.count + 1
               

            
            

    def shutdown_optitrack(self):
        self.opt_client.shutdown()
        self.opti.close()
            

def main():
    return
       
    
if __name__ == '__main__':
    main()