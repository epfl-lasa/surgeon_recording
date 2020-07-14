import sys
import pathlib
import time
import numpy as np
import pandas as pd
import os
import cv2
import pyrealsense2 as rs
from os.path import join
from threading import Thread
from threading import Event
import signal

# deifne the directory of the emgAcquireClient python_module 
emgAcquire_dir = r"C:\Users\OptitrackTrio\Documents\GitHub\surgeon_recording\source\emgAcquire\python_module"
# append the path including the directory of the python_module
sys.path.append(emgAcquire_dir)
# import the module
import emgAcquireClient

# deifne the directory of the emgAcquireClient python_module 
NatNetClient_dir = r"C:\Users\OptitrackTrio\Documents\NatNetSDK\Samples\PythonClient"
# append the path including the directory of the python_module
sys.path.append(NatNetClient_dir)
# import the module
from NatNetClient import NatNetClient


class Recorder(object):
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.recording = False

        ######## User input ######
        self.task_folder = input("Enter task name : ")
        self.exp_folder = join(self.data_folder, self.task_folder)
        if not os.path.exists(self.exp_folder):
            os.makedirs(self.exp_folder)

        self.emg_data = []
        self.opt_data = []
        # init all sensors
        self.init_camera()
        self.init_emg()
        self.init_optitrack()

        # initiliaze the threads
        self.stop_event = Event()
        self.recording_threads = []
        self.recording_threads.append(Thread(target=self.record_camera))
        self.recording_threads.append(Thread(target=self.record_emg))
        #self.recording_threads.append(Thread(target=self.record_optitrack))

        for t in self.recording_threads:
            t.start()

    def stop_recording_handler(self):
        # Handle any cleanup here
        print('recording stop')
        self.recording = False
        self.write_data()
        self.stop_event.set()

    def init_optitrack(self):
        self.recorded_frames = ['blade', 'wrist', 'elbow']
        self.opt_data = []
    
    def init_camera(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        color_path = join(self.exp_folder, 'rgb.avi')
        depth_path = join(self.exp_folder, 'depth.avi')
        self.colorwriter = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
        self.depthwriter = cv2.VideoWriter(depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)

        self.pipeline.start(self.config)

    def init_emg(self):
        # define number of channels to acquire
        self.nb_ch = 9
        emg_ip = "localhost"
        # create an emgClient object for acquiring the data
        self.emgClient = emgAcquireClient.emgAcquireClient(svrIP=emg_ip, nb_channels=self.nb_ch)
        # initialize the node
        self.emgClient.initialize()
        self.emg_data = []

    def record_camera(self):
        while not self.stop_event.wait(0.001):
            if self.recording:
                # Wait for a coherent pair of frames: depth and color
                frames = self.pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                if not depth_frame or not color_frame:
                    return

                # Convert images to numpy arrays
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())

                # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

                # write the image
                self.colorwriter.write(color_image)
                self.depthwriter.write(depth_colormap)

                # Stack both images horizontally
                #images = np.hstack((color_image, depth_colormap))

                # # Show images
                #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
                #cv2.imshow('RealSense', images)
                #cv2.waitKey(1)

    def record_emg(self):
        # start filling the buffer
        self.emgClient.start()
        while not self.stop_event.wait(0.001):
            # acquire the signals from the buffer
            emg_array = self.emgClient.getSignals()
            if self.recording:
                # append the array with the new data
                if len(self.emg_data) > 1:
                    prev_time = self.emg_data[-1][0]
                else:
                    prev_time = self.start_time
                last_sample_time = time.time()
                dt = (last_sample_time - prev_time)/len(emg_array[0])
                for i in range(len(emg_array[0])):
                    data = []
                    t = prev_time + (i+1) * dt
                    data.append(t)
                    # keep the updating period
                    data.append(t - self.start_time)
                    data = data + emg_array[:, i].tolist()
                    # append everything
                    self.emg_data.append(data)

    def record_optitrack(self):
        while not self.stop_event.wait(0.001):
            if self.recording:
                absolute_time = time.time()
                data = [absolute_time, absolute_time - self.start_time]
                #for f in self.recorded_frames:
                    
                self.opt_data.append(data)

    def record(self):
        input("Press enter to start recording...")
        print('Start recording')
        self.emg_data = []
        self.opt_data = []
        self.start_time = time.time()
        self.recording = True

    def write_data(self):
        print('Writing data')

        # emg data
        if self.emg_data:
            emg_header = ["emg" + str(i) for i in range(self.nb_ch)]
            emg_header = ["absolute_time", "relative_time"] + emg_header
            pd.DataFrame(self.emg_data).to_csv(join(self.exp_folder, "emg.csv"), header=emg_header)
        else:
            print("No EMG data recorded")    

        # optitrack data
        if self.opt_data:
            opt_header = ["absolute_time", "relative_time"]
            for f in self.recorded_frames:
                opt_header = opt_header + [f + "_x", f + "_y", f + "_z", f + "_qw", f + "_qx", f + "_qy", f + "_qz"]
            pd.DataFrame(self.opt_data).to_csv(join(self.exp_folder, "opt.csv"), header=opt_header)
        else:
            print("No optitrack data recorded")

    def shutdown(self):
        self.emgClient.shutdown()
        self.colorwriter.release()
        self.depthwriter.release()
        self.pipeline.stop()


def main(args=None):
    # define the folder
    subject_folder = "fleur"

    # create variables
    data_folder = join("..", "..", "..", "data", subject_folder)
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    recorder = Recorder(data_folder)
    recorder.record()
    while(True):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            recorder.stop_recording_handler()
            break

    for t in recorder.recording_threads:
        t.join()
    recorder.shutdown()
    
    
if __name__ == '__main__':
    main()