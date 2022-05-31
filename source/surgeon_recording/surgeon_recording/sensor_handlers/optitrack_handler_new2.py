import time
from NatNetClient import NatNetClient
import csv
import numpy as np
import os
from os.path import join
import json



class OptitrackHandlerNew2:
    def __init__(self, csv_path1, csv_path2):
        self.csv_path_optitrack1 = csv_path1
        self.csv_path_optitrack2 = csv_path2
        #self.csv_path_optitrack3 = csv_path3

        self.data_dict = []
        self.index_optitrack = []
        self.rel_time = []
        self.received_id = []

        self.count = 0
        self.count2 = 0

        self.parameters_optitrack=[]
        self.get_parameters_optitrack()
        self.running_optitrack = (self.parameters_optitrack['status'] == 'on')

        if self.running_optitrack:
            header_ini = ["index", "relative_time", "absolute_time"]
            self.header_optitrack1 = ["nb of frame loops", "nb of body loops", "number of points", "value last index"]
            self.header_optitrack2= header_ini +  self.parameters_optitrack['header']
                        
            self.data_optitrack = []
        
            self.received_frames = {}
            self.received_body = {}

            for frame in self.parameters_optitrack['frames']:
                label = frame['label']
                self.received_body[frame['streaming_id']] = {'label': label, 'position': [], 'orientation': [],  'tmp' : []}
                self.received_frames = {'timestamp2': [], 'frame_number': []}



            self.opt_client = NatNetClient()
            self.opt_client.set_print_level(0)

            self.opti1 = open(self.csv_path_optitrack1, 'w', newline='')
            self.writer_opti1 = csv.writer(self.opti1)
            self.writer_opti1.writerow(self.header_optitrack1)
            self.row_optitrack1 = []

            self.opti2 = open(self.csv_path_optitrack2, 'w', newline='')
            self.writer_opti2 = csv.writer(self.opti2)
            self.writer_opti2.writerow(self.header_optitrack2)
            self.row_optitrack2 = []

            #self.opti3 = open(self.csv_path_optitrack3, 'w', newline='')
            #self.writer_opti3 = csv.writer(self.opti3)
            #self.writer_opti3.writerow(self.header_optitrack3)
            #self.row_optitrack3 = []

            # Configure the streaming client to call our rigid body handler on the emulator to send data out.
            self.opt_client.new_frame_listener = self.receive_new_frame
            self.opt_client.rigid_body_listener = self.receive_rigid_body_frame
            # Start up the streaming client now that the callbacks are set up.
            # This will run perpetually, and operate on a separate thread.
            self.opt_client.run()
            self.start_time_opti = time.time()
            self.writer_opti2.writerow([self.start_time_opti])

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
            self.received_frames['timestamp2'] = data_dict["timestamp"]
            self.received_frames['frame_number'].append(data_dict["frame_number"])
            #self.received_frames[16]['test'] = data_dict[ "tracked_models_changed"]
            self.count = self.count+1
            
            #self.row_optitrack1 = [data_dict["timestamp"], data_dict["frame_number"] ]
            #self.writer_opti1.writerow(self.row_optitrack1)
            #self.row_optitrack1= []

            if len(self.received_frames['frame_number']) > 0:
                self.row_optitrack2 = [self.received_frames['frame_number'][-1]-self.received_frames['frame_number'][0], data_dict["timestamp"], time.time()]
            else: 
                self.row_optitrack2 = [0, time.time()]

            
            for id in self.received_id:
                
                for i in range(len(self.received_body[id]['position'])):
                    if len(self.received_body[id]['tmp']) >1 and self.received_body[id]['tmp'][0] == self.received_body[id]['tmp'][1]:
                        self.row_optitrack2.append(0)
                    else:    
                        self.row_optitrack2.append(self.received_body[id]['position'][i])
                for j in range(len(self.received_body[id]['orientation'])):
                    if len(self.received_body[id]['tmp']) >1 and self.received_body[id]['tmp'][0] == self.received_body[id]['tmp'][1]:
                        self.row_optitrack2.append(0)
                    else:
                        self.row_optitrack2.append(self.received_body[id]['orientation'][j])
            

            self.writer_opti2.writerow(self.row_optitrack2)
            self.row_optitrack2= [] 
            self.received_id =[]

            #print("FRAME")  

            #print("new frame")
            for id in self.received_id: 
                self.received_body[id]['position'] = 0
                self.received_body[id]['orientation'] =0 



    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body_frame(self, id, position, rotation):      
        if id in self.received_body.keys():
            self.received_id.append(id)
            self.received_body[id]['position'] = position
            self.received_body[id]['orientation'] = rotation

            self.count2 = self.count2 + 1
            self.received_body[id]['tmp'].append(position[0])

            if len(self.received_body[id]['tmp']) > 2:
                self.received_body[id]['tmp'] = [self.received_body[id]['tmp'][-2], self.received_body[id]['tmp'][-1]]
           
            #print("BODY")

    #def make_csv_optitrack(self)

            
    def shutdown_optitrack(self):
        self.opt_client.shutdown()
        print("optitrack closed cleanly")
        self.row_optitrack1 = [self.count, self.count2, len(self.received_frames['frame_number']) ,self.received_frames['frame_number'][-1] - self.received_frames['frame_number'][0] ]
        self.writer_opti1.writerow(self.row_optitrack1)
        print(self.count)
        print(self.count2)
        print(len(self.received_frames['frame_number']))
        print(self.received_frames['frame_number'][-1] - self.received_frames['frame_number'][0])
        self.opti1.close()
        self.opti2.close()
        #self.opti3.close()

def main():
    return
       
    
if __name__ == '__main__':
    main()