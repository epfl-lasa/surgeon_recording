import sys
import pathlib
import time
import numpy as np
import csv
import os
import cv2
import pyrealsense2 as rs
from os.path import join
from threading import Thread
from threading import Event
import signal
from surgeon_recording.NatNetClient import NatNetClient
import pandas as pd
from multiprocessing import Lock
from collections import deque

# deifne the directory of the emgAcquireClient python_module 
emgAcquire_dir = r"C:\Users\buschbapti\Documents\GitHub\surgeon_recording\source\emgAcquire\python_module"
#emgAcquire_dir = "/home/buschbapti/Documents/Zeiss/surgeon_recording/source/emgAcquire/python_module"

# append the path including the directory of the python_module
sys.path.append(emgAcquire_dir)
# import the module
import emgAcquireClient

class Recorder(object):
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.exp_folder = ""
        self.recording = False
        self.lock = Lock()

        # create csv writers
        self.writers = {}
        self.received_frames = {}
        self.emg_header = []
        self.opt_header = []
        self.emg_data = deque(maxlen=2000)
        self.opt_data = []
        self.buffered_depth = []
        self.buffered_rgb = []
        self.camera_index = 0
        self.opt_index = 0
        self.emg_init = False
        self.timeout = 0.1
        self.start_time = time.time()
        # init all sensors
        self.init_camera()
        self.init_emg()
        self.init_optitrack()

        # initiliaze the threads
        self.stop_event = Event()
        self.recording_threads = []
        self.recording_threads.append(Thread(target=self.record_camera))
        self.recording_threads.append(Thread(target=self.record_emg))
        self.recording_threads.append(Thread(target=self.record_optitrack))

        for t in self.recording_threads:
            t.start()

    def init_recording_folder(self, folder):
        self.exp_folder = join(self.data_folder, folder)
        if not os.path.exists(self.exp_folder):
            os.makedirs(self.exp_folder)    

    def init_optitrack(self):
        ids = {2: "test", 3: "test2",}
        self.opt_header = ["index", "absolute_time", "relative_time"]
        for key, label in ids.items():
            self.received_frames[key] = {"label": label, "position": [], "orientation": [], "timestamp": 0}
            self.opt_header = self.opt_header + [label + "_x", label + "_y", label + "_z", label + "_qw", label + "_qx", label + "_qy", label + "_qz"]

        self.opt_client = NatNetClient()
        # Configure the streaming client to call our rigid body handler on the emulator to send data out.
        self.opt_client.newFrameListener = self.receive_frame
        self.opt_client.rigidBodyListener = self.receive_rigid_body
        # Start up the streaming client now that the callbacks are set up.
        # This will run perpetually, and operate on a separate thread.
        self.opt_client.run()

    def init_optitrack_writer(self):
        f = open(join(self.exp_folder, "opt.csv"), 'w', newline='')
        self.writers["opt"] = {"file": f, "writer": csv.writer(f)}
        self.writers["opt"]["writer"].writerow(self.opt_header)

    def init_camera(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        try:
            self.pipeline.start(self.config)
        except:
            print("Error initializing the camera")

    def init_camera_writer(self):
        color_path = join(self.exp_folder, 'rgb.avi')
        depth_path = join(self.exp_folder, 'depth.avi')
        self.colorwriter = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
        self.depthwriter = cv2.VideoWriter(depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)

        f = open(join(self.exp_folder, "camera.csv"), 'w', newline='')
        self.writers["camera"] = {"file": f, "writer": csv.writer(f)}
        self.writers["camera"]["writer"].writerow(["index", "absolute_time", "relative_time"])

    def init_emg(self):
        # define number of channels to acquire
        self.nb_ch = 9
        emg_ip = "localhost"
        # create an emgClient object for acquiring the data
        self.emgClient = emgAcquireClient.emgAcquireClient(svrIP=emg_ip, nb_channels=self.nb_ch)
        # initialize the node
        init_value = self.emgClient.initialize()
        self.emg_init = init_value == 0

        self.emg_header = ["emg" + str(i) for i in range(self.nb_ch)]
        self.emg_header = ["index", "absolute_time", "relative_time"] + self.emg_header
        
    def init_emg_writer(self):
        f = open(join(self.exp_folder, "emg.csv"), 'w', newline='')
        self.writers["emg"] = {"file": f, "writer": csv.writer(f)}
        self.writers["emg"]["writer"].writerow(self.emg_header)

    def record_camera(self):
        print("Starting recording camera")
        while not self.stop_event.wait(0.001):

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

            self.buffered_rgb = color_image
            self.buffered_depth = depth_colormap

            absolute_time = time.time()
            data = [self.camera_index + 1, absolute_time, absolute_time - self.start_time]
            self.camera_index = data[0]
                
            if self.recording:
                self.writers["camera"]["writer"].writerow(data)
                # write the images
                self.colorwriter.write(color_image)
                self.depthwriter.write(depth_colormap)

    def record_emg(self):
        # start filling the buffer
        print("Starting recording EMG")
        if self.emg_init:
            self.emgClient.start()
            while not self.stop_event.wait(0.001):
                # acquire the signals from the buffer
                emg_array = self.emgClient.getSignals()
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
                    self.emg_data.append(data)

                    if self.recording:
                        # append everything
                        self.writers["emg"]["writer"].writerow(data)

    def record_optitrack(self):
        print("Starting recording Optitrack")
        while not self.stop_event.wait(0.01):
            absolute_time = time.time()
            data = [self.opt_index + 1, absolute_time, absolute_time - self.start_time]
            for key, f in self.received_frames.items():
                if absolute_time - f["timestamp"] < self.timeout:
                    for pos in f["position"]:
                        data.append(pos)
                    for rot in f["orientation"]:
                        data.append(rot)
                else:
                    print("Frame " + f["label"] + " not visible")
                    return
            self.opt_index = data[0]
            self.opt_data = [data]

            print("Here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            if self.recording:
                print("good!!!!!!!!!!!!!!")
                self.writers["opt"]["writer"].writerow(data)

    def get_buffered(self, data, header):
        if data:
            return pd.DataFrame(data=np.array(data)[:,1:], index=np.array(data)[:,0], columns=header[1:])
        return pd.DataFrame(columns=header[1:])

    def get_buffered_emg(self):
        return self.get_buffered(self.emg_data, self.emg_header)

    def get_buffered_opt(self):
        return self.get_buffered(self.opt_data, self.opt_header)

    def get_buffered_rgb(self):
        return cv2.imencode('.jpg', self.buffered_rgb)[1]

    def get_buffered_depth(self):
        return cv2.imencode('.jpg',self.buffered_depth)[1]

    def record(self, folder):
        print('Start recording')
        with self.lock:
            self.init_recording_folder(folder)
            self.init_camera_writer()
            self.init_emg_writer()
            self.init_optitrack_writer()
            self.emg_data = deque(maxlen=2000)
            self.opt_data = []
            self.camera_index = 0
            self.opt_index = 0
            self.start_time = time.time()
            self.recording = True
    
    def stop_recording(self):
        # Handle any cleanup here
        self.recording = False
        self.colorwriter.release()
        self.depthwriter.release()
        for key, value in self.writers.items():
            value['file'].close()

    def shutdown(self):
        print("Shutdown initiated")
        if self.emg_init:
            self.emgClient.shutdown()
        print("EMG shutdown")
        self.colorwriter.release()
        self.depthwriter.release()
        self.pipeline.stop()
        print("Camera shutdown")
        self.opt_client.shutdown()
        print("Optitrack shutdown")
        for _, value in self.writers.items():
            value["file"].close()

    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body(self, id, position, rotation):
        self.received_frames[id]["timestamp"] = time.time()
        self.received_frames[id]["position"] = position
        self.received_frames[id]["orientation"] = rotation

    # This is a callback function that gets connected to the NatNet client and called once per mocap frame.
    def receive_frame(self, frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                      labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
        return


# def main(args=None):
#     # define the folder
#     subject_folder = "fleur"

#     # create variables
#     data_folder = join("..", "..", "..", "data", subject_folder)
#     if not os.path.exists(data_folder):
#         os.makedirs(data_folder)

#     recorder = Recorder(data_folder)
#     recorder.record()
#     while(True):
#         try:
#             time.sleep(1)
#         except KeyboardInterrupt:
#             recorder.stop_recording_handler()
#             break

#     recorder.shutdown()
#     for t in recorder.recording_threads:
#         t.join()

    
# if __name__ == '__main__':
#     main()