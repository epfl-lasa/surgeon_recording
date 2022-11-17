import time
from surgeon_recording.sensor_handlers.recorder_v2_PDM.NatNetClient import NatNetClient
import csv



class OptitrackHandlerNew(object):
    def __init__(self):
        self.data_dict = []
        ################ SET THE TOOL YOU WANT TO USE FOR THE TEST############################## 
        # here the id and name are hardcoded (they have to correspond to id and name defined on motive)
        self.received_frames = {'3': {'label': 'tweezers', 'position': [], 'orientation': [], 'timestamp': [], 'timestamp2': [], 'is_recording':[], 'timecode':[], 'timecode_sub': [], 'frame_number': []}}

        self.opt_client = NatNetClient()
        self.opt_client.set_print_level(0)

        #################### adapt the path for the test you want to do ####################
        self.csv_path = "/Users/LASA/Documents/Recordings/surgeon_recording/data/test_optitrack_new_recorder/test_1.csv"
        self.f = open(self.csv_path, 'w', newline='')
        self.writer = csv.writer(self.f)

        ##################### adapt the header depednding on which data you want ##########
        header = ['index', 'timestamp', 'timestamp2', 'timecode','timecode_sub', 'Isrecording']
        self.writer.writerow(header)



        # Configure the streaming client to call our rigid body handler on the emulator to send data out.
        self.opt_client.new_frame_listener = self.receive_new_frame
        self.opt_client.rigid_body_listener = self.receive_rigid_body_frame
        # Start up the streaming client now that the callbacks are set up.
        # This will run perpetually, and operate on a separate thread.
        self.opt_client.run()

        
    


   # This is a callback function that gets connected to the NatNet client and called once per mocap frame.
    def receive_new_frame(self, data_dict):
        # possible data we can get with this callback function:
        # order_list = ["frame_number", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
        #               "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "is_recording", "trackedModelsChanged"]

        # get the whole set of data in data_dict
        self.data_dict.append(data_dict) 
        
        # store the data we want from data_dict
        self.received_frames['3']['timestamp2'].append(data_dict["timestamp"])
        self.received_frames['3']['timecode'].append(data_dict["timecode"])
        self.received_frames['3']['timecode_sub'].append(data_dict["timecode_sub"])
        self.received_frames['3']['is_recording'].append(data_dict["is_recording"])
        self.received_frames['3']['frame_number'].append(data_dict["frame_number"])

        # put data i na row to write in a csv file
        # the frame number does not start from 0 so remove first frame_number to start from 0 in the csv
        # the relative timestamps do not start from 0 (start from the moment the software was on) but this was dealt with in the psot processing
        # (the interesting thing is to get accurate time measurement, as it is relative the reference does not matter) 
        row = [data_dict["frame_number"]- self.received_frames['3']['frame_number'][0], self.received_frames['3']['timestamp'][-1], data_dict["timestamp"], data_dict["timecode"],data_dict["timecode_sub"], data_dict["is_recording"]]
        self.writer.writerow(row) 



    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body_frame(self, id, position, rotation):
        id = '3'
        #here we get the position and quaternions data for the tools 
        #a measure of absolute time using the computer time was taken to test the accuracy but it was seen that
        # the frequency of acquisition obtained using this time does not correspond to the frequency obtained using
        # the relative time measurements. The relative time measurements are reliable as they are linked to the frames,
        # so taking the absolute time like this is too dependant of the process and the computer.
        self.received_frames[id]['timestamp'].append(time.time())
        self.received_frames[id]['position'].append(position)
        self.received_frames[id]['orientation'].append(rotation)

        

def main():
       
    start_time = time.time()
    handler = OptitrackHandlerNew()

    is_looping = True
    # set a time limit for the recording (here 10s)
    while is_looping:
        if time.time() - start_time > 10:
            is_looping = False
            handler.opt_client.shutdown()
            handler.f.close()
            
    # check how many frames we got
    print(len(handler.received_frames['3']['timestamp']))
    print(len(handler.data_dict))
    
    ###########################################################################################################
    # OTHER TEST: write verything at the end to see if it improves the performances:
    # (did not see a big difference and here we have to store every data, we can never clean the variable, so not best solution)

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