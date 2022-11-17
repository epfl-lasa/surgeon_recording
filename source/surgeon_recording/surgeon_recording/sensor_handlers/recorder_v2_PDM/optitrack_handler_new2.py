import time
from surgeon_recording.sensor_handlers.recorder_v2_PDM.NatNetClient import NatNetClient
import csv
import numpy as np
import os
from os.path import join
import json



class OptitrackHandlerNew2:
    def __init__(self, csv_path1, csv_path2):
        # the csv  files are desifned in the main recorder
        self.csv_path_optitrack1 = csv_path1
        self.csv_path_optitrack2 = csv_path2
        
        self.data_dict = []
        self.index_optitrack = []
        self.rel_time = []
        self.received_id = []

        self.count = 0
        self.count2 = 0
        self.parameters_optitrack=[]
        # read the parameters in the parameter file (name of tools and id)
        self.get_parameters_optitrack()
        self.running_optitrack = (self.parameters_optitrack['status'] == 'on')

        if self.running_optitrack:
            # prepare headers for the two files
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

            # prepare to write in the csv files
            self.opti1 = open(self.csv_path_optitrack1, 'w', newline='')
            self.writer_opti1 = csv.writer(self.opti1)
            self.writer_opti1.writerow(self.header_optitrack1)
            self.row_optitrack1 = []

            self.opti2 = open(self.csv_path_optitrack2, 'w', newline='')
            self.writer_opti2 = csv.writer(self.opti2)
            self.writer_opti2.writerow(self.header_optitrack2)
            self.row_optitrack2 = []


            # Configure the streaming client to call our rigid body handler on the emulator to send data out.
            self.opt_client.new_frame_listener = self.receive_new_frame
            self.opt_client.rigid_body_listener = self.receive_rigid_body_frame
            # Start up the streaming client now that the callbacks are set up.
            # This will run perpetually, and operate on a separate thread.
            self.opt_client.run()

            # write a first absolute time reference when we start the sensor
            self.start_time_opti = time.time()
            self.writer_opti2.writerow([self.start_time_opti])

    # gets the status of the sensor
    def read_config_file(self, sensor_name):
        filepath = os.path.abspath(os.path.dirname(__file__))
        with open(join(filepath, '..', '..', '..','config', 'sensor_parameters.json'), 'r') as paramfile:
            config = json.load(paramfile)
        if not sensor_name in config.keys():
            config[sensor_name] = {}
            config[sensor_name]['status'] = 'off'
        return config[sensor_name]
     
    # gets the names of the activated tools
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
        # possible data from this function:
        # order_list = ["frame_number", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
        #               "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "is_recording", "trackedModelsChanged"]

        # get relative time and frame number
            self.received_frames['timestamp2'] = data_dict["timestamp"]
            self.received_frames['frame_number'].append(data_dict["frame_number"])
            self.count = self.count+1
            
          
            # if we have a frame: write relative time, frame number and absolute time
            if len(self.received_frames['frame_number']) > 0:
                self.row_optitrack2 = [self.received_frames['frame_number'][-1]-self.received_frames['frame_number'][0], data_dict["timestamp"], time.time()]
            # if no frame (1st call): write 0 and absolute time
            else: 
                self.row_optitrack2 = [0, time.time()]

            #for all the tools and the data output (x,y,z,qx,qy,qz,qw), 
            # enleve doublon (?)
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

           # reset variables
            for id in self.received_id: 
                self.received_body[id]['position'] = 0
                self.received_body[id]['orientation'] =0 



    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body_frame(self, id, position, rotation):      
        if id in self.received_body.keys():
            # get the id of the tools, th eposition and quaternion values
            self.received_id.append(id)
            self.received_body[id]['position'] = position
            self.received_body[id]['orientation'] = rotation

            self.count2 = self.count2 + 1
            self.received_body[id]['tmp'].append(position[0])

            # when we have more than two values saved, keep only the last two 
            # (to avoid filling the memory, and to be able to compare the last 2 values to know if we missed a rigid body frame)
            if len(self.received_body[id]['tmp']) > 2:
                self.received_body[id]['tmp'] = [self.received_body[id]['tmp'][-2], self.received_body[id]['tmp'][-1]]
           

            
    def shutdown_optitrack(self):
        self.opt_client.shutdown()
        print("optitrack closed cleanly")
        # write the statistics
        self.row_optitrack1 = [self.count, self.count2, len(self.received_frames['frame_number']) ,self.received_frames['frame_number'][-1] - self.received_frames['frame_number'][0] ]
        self.writer_opti1.writerow(self.row_optitrack1)
        print(self.count)
        print(self.count2)
        print(len(self.received_frames['frame_number']))
        print(self.received_frames['frame_number'][-1] - self.received_frames['frame_number'][0])
        self.opti1.close()
        self.opti2.close()

def main():
    return
       
    
if __name__ == '__main__':
    main()