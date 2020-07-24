import sys
import time
import numpy as np
import os
import cv2
from os.path import join
from threading import Thread
from threading import Event
import signal
from surgeon_recording.NatNetClient import NatNetClient
import pandas as pd
from collections import deque
import zmq
from surgeon_recording.camera_handler import CameraHandler
from surgeon_recording.emg_handler import EMGHandler

class Recorder(object):
    def __init__(self, data_folder):
        self.recording = False
        self.data_folder = data_folder
        self.exp_folder = ""

        self.emg_data = deque(maxlen=2000)
        self.opt_data = deque(maxlen=100)
        self.buffered_images = {}
        self.start_time = time.time()
        # init all sensors
        self.socket_recorders = []
        self.init_camera()
        self.init_emg()
        #self.init_optitrack()

        # initiliaze the threads
        self.stop_event = Event()
        self.recording_threads = []
        self.recording_threads.append(Thread(target=self.get_camera_data))
        self.recording_threads.append(Thread(target=self.get_emg_data))
        #self.recording_threads.append(Thread(target=self.record_optitrack))

        for t in self.recording_threads:
            t.start()

    def init_recording_folder(self, folder):
        self.exp_folder = join(self.data_folder, folder)
        if not os.path.exists(self.exp_folder):
            os.makedirs(self.exp_folder)    

    def init_camera(self):
        ip = "127.0.0.1"
        port = "5556"
        context = zmq.Context()
        self.socket_camera = context.socket(zmq.SUB)
        self.socket_camera.connect("tcp://%s:%s" % (ip, port))
        self.socket_camera.setsockopt(zmq.SUBSCRIBE, b'rgb')
        self.socket_camera.setsockopt(zmq.SUBSCRIBE, b'depth')

        port = "5557"
        context = zmq.Context()
        socket_camera_recorder = context.socket(zmq.REQ)
        socket_camera_recorder.connect("tcp://%s:%s" % (ip, port))
        self.socket_recorders.append(socket_camera_recorder)

    #def init_optitrack(self):
        # ids = {2: "test", 3: "test2",}
        # self.opt_header = ["index", "absolute_time", "relative_time"]
        # for key, label in ids.items():
        #     self.received_frames[key] = {"label": label, "position": [], "orientation": [], "timestamp": 0}
        #     self.opt_header = self.opt_header + [label + "_x", label + "_y", label + "_z", label + "_qw", label + "_qx", label + "_qy", label + "_qz"]

        # self.opt_client = NatNetClient()
        # # Configure the streaming client to call our rigid body handler on the emulator to send data out.
        # self.opt_client.newFrameListener = self.receive_frame
        # self.opt_client.rigidBodyListener = self.receive_rigid_body
        # # Start up the streaming client now that the callbacks are set up.
        # # This will run perpetually, and operate on a separate thread.
        # self.opt_client.run()

    

    def init_emg(self):
        ip = "127.0.0.1"
        port = "5558"
        context = zmq.Context()
        self.socket_emg = context.socket(zmq.SUB)
        self.socket_emg.connect("tcp://%s:%s" % (ip, port))
        self.socket_emg.setsockopt(zmq.SUBSCRIBE, b'emg')

        port = "5559"
        context = zmq.Context()
        socket_emg_recorder = context.socket(zmq.REQ)
        socket_emg_recorder.connect("tcp://%s:%s" % (ip, port))
        self.socket_recorders.append(socket_emg_recorder)


    def get_camera_data(self):
        while not self.stop_event.is_set():
            data = CameraHandler.receive_data(self.socket_camera)
            self.buffered_images.update(data)

    def get_emg_data(self):
        while not self.stop_event.is_set():
            signal = EMGHandler.receive_data(self.socket_emg)
            for s in signal['emg']:
                self.emg_data.append(s)

    # def record_optitrack(self):
    #     print("Starting recording Optitrack")
    #     while not self.stop_event.wait(0.01):
    #         absolute_time = time.time()
    #         data = [self.opt_index + 1, absolute_time, absolute_time - self.start_time]
    #         for key, f in self.received_frames.items():
    #             if absolute_time - f["timestamp"] < self.timeout:
    #                 for pos in f["position"]:
    #                     data.append(pos)
    #                 for rot in f["orientation"]:
    #                     data.append(rot)
    #             else:
    #                 print("Frame " + f["label"] + " not visible")
    #                 return
    #         self.opt_index = data[0]
    #         self.opt_data = [data]
    #         if self.recording:
    #             self.writers["opt"]["writer"].writerow(data)

    def get_buffered(self, data, header):
        if data:
            return pd.DataFrame(data=np.array(data)[:,1:], index=np.array(data)[:,0], columns=header[1:])
        return pd.DataFrame(columns=header[1:])

    def get_buffered_emg(self):
        header = ["index", "absolute_time", "relative_time"] + ['emg' + str(i) for i in range(9)]
        return self.get_buffered(self.emg_data, header)

    def get_buffered_opt(self):
        return self.get_buffered(self.opt_data, self.opt_header)

    def get_buffered_rgb(self):
        return cv2.imencode('.jpg', self.buffered_images['rgb'])[1]

    def get_buffered_depth(self):
        return cv2.imencode('.jpg', self.buffered_images['depth'])[1]

    def record(self, folder):
        self.recording = True
        self.init_recording_folder(folder)
        self.emg_data = deque(maxlen=2000)
        self.opt_data = deque(maxlen=100)
        message = {'recording': True, 'folder': os.path.abspath(self.exp_folder), 'start_time': time.time()}
        for s in self.socket_recorders:
            s.send_json(message)
            s.recv_string()
    
    def stop_recording(self):
        self.recording = False
        message = {'recording': False}
        for s in self.socket_recorders:
            s.send_json(message)
            s.recv_string()

    def shutdown(self):
        self.stop_event.set()
        self.socket_camera.close()
        self.socket_emg.close()
        for s in self.socket_recorders:
            s.close()

    # # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    # def receive_rigid_body(self, id, position, rotation):
    #     self.received_frames[id]["timestamp"] = time.time()
    #     self.received_frames[id]["position"] = position
    #     self.received_frames[id]["orientation"] = rotation

    # # This is a callback function that gets connected to the NatNet client and called once per mocap frame.
    # def receive_frame(self, frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
    #                   labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
    #     return


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