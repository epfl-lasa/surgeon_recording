import time
from NatNetClient import NatNetClient
import csv



class OptitrackHandlerNew(object):
    def __init__(self):
        self.data_dict = []

        self.opt_client = NatNetClient()
        self.opt_client.set_print_level(0)

        self.csv_path_optitrack = "/Users/LASA/Documents/Recordings/surgeon_recording/data/new_recorder/optitrack_1.csv"
        self.opti = open(self.csv_path_optitrack, 'w', newline='')
        self.writer_opti = csv.writer(self.opti)
        #header_opti = ['index', 'timestamp', 'timestamp2', 'timecode','timecode_sub', 'Isrecording']
        self.writer.writerow(self.header_optitrack)
        self.row_optitrack = []


        # Configure the streaming client to call our rigid body handler on the emulator to send data out.
        self.opt_client.new_frame_listener = self.receive_new_frame
        self.opt_client.rigid_body_listener = self.receive_rigid_body_frame
        # Start up the streaming client now that the callbacks are set up.
        # This will run perpetually, and operate on a separate thread.
        self.opt_client.run()

        
    


    # This is a callback function that gets connected to the NatNet client and called once per mocap frame.
    def receive_new_frame(self, id, data_dict):
        # order_list = ["frame_number", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
        #               "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "is_recording", "trackedModelsChanged"]
        id_frame = self.received_frames.keys()[0]
        self.row_optitrack.append(data_dict["frame_number"]- self.received_frames[id_frame]['frame_number'][0])
        #self.data_dict.append(data_dict) #should get the info for all the things of order list in data_dict donc timestamp
        if id in self.received_frames.keys():
            #self.received_frames[id]['timestamp2'].append(data_dict["timestamp"])
            #self.received_frames[id]['frame_number'].append(data_dict["frame_number"])
            self.row_optitrack.append(data_dict["timestamp"])
            
        self.writer_opti.writerow(self.row_optitrack)



    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body_frame(self, id, position, rotation):
        id_frame = self.received_frames.keys()[0]
        self.received_frames[id_frame]['timestamp'].append(time.time())
        self.row_optitrack.append(self.received_frames[id_frame]['timestamp'],)
        
        if id in self.received_frames.keys():
            self.received_frames[id]['timestamp'].append(time.time())
            self.received_frames[id]['position'].append(position)
            self.received_frames[id]['orientation'].append(rotation)
            self.row_optitrack.append(position, rotation)

        self.writer_opti.writerow(self.row_optitrack) 
        

def main():
       
    start_time = time.time()
    handler = OptitrackHandlerNew()

    is_looping = True
    
    while is_looping:
        if time.time() - start_time > 3:
            is_looping = False
            handler.opt_client.shutdown()
            handler.f.close()
            

    
    # print(handler.received_frames['3']['timestamp'])
    print(len(handler.received_frames['3']['timestamp']))
    print(len(handler.data_dict))
    
    # write everything at the end:
    # csv_path = "/Users/LASA/Documents/Recordings/surgeon_recording/data/test_optitrack_new_recorder/test_0.csv"

    # f = open(csv_path, 'w', newline='')
    # writer = csv.writer(f)
    # header = ['index', 'timestamp', 'timestamp2', 'is_recording', 'timecode']
    # writer.writerow(header)
    # for m in range(len(handler.received_frames['3']['timestamp'])):
    #     row = [m, handler.received_frames['3']['timestamp'][m], handler.received_frames['3']['timestamp2'][m], handler.data_dict[m]["is_recording"], handler.data_dict[m]["timecode"]]
    #     writer.writerow(row) 
    
    # f.close()

    



if __name__ == '__main__':
    main()