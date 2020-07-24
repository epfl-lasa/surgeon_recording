import sys
import time
import numpy as np
import os
import cv2
from os.path import join
from threading import Thread
from threading import Event
import pandas as pd
from collections import deque
import zmq
from surgeon_recording.camera_handler import CameraHandler
from surgeon_recording.emg_handler import EMGHandler
from surgeon_recording.optitrack_handler import OptitrackHandler

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
        self.init_optitrack()

        # initiliaze the threads
        self.stop_event = Event()
        self.recording_threads = []
        self.recording_threads.append(Thread(target=self.get_camera_data))
        self.recording_threads.append(Thread(target=self.get_emg_data))
        self.recording_threads.append(Thread(target=self.get_optitrack_data))

        for t in self.recording_threads:
            t.start()

    def init_recording_folder(self, folder):
        self.exp_folder = join(self.data_folder, folder)
        if not os.path.exists(self.exp_folder):
            os.makedirs(self.exp_folder)    

    def init_camera(self):
        parameters = CameraHandler.get_parameters()
        ip = parameters["streaming_ip"]
        port = parameters["port"]

        context = zmq.Context()
        self.socket_camera = context.socket(zmq.SUB)
        self.socket_camera.connect("tcp://%s:%s" % (ip, port))
        self.socket_camera.setsockopt(zmq.SUBSCRIBE, b'rgb')
        self.socket_camera.setsockopt(zmq.SUBSCRIBE, b'depth')

        context = zmq.Context()
        socket_camera_recorder = context.socket(zmq.REQ)
        socket_camera_recorder.connect("tcp://%s:%s" % (ip, port + 1))
        self.socket_recorders.append(socket_camera_recorder)

    def init_optitrack(self):
        parameters = OptitrackHandler.get_parameters()
        ip = parameters["streaming_ip"]
        port = parameters["port"]

        context = zmq.Context()
        self.socket_optitrack = context.socket(zmq.SUB)
        self.socket_optitrack.connect("tcp://%s:%s" % (ip, port))
        self.socket_optitrack.setsockopt(zmq.SUBSCRIBE, b'optitrack')

        context = zmq.Context()
        socket_optitrack_recorder = context.socket(zmq.REQ)
        socket_optitrack_recorder.connect("tcp://%s:%s" % (ip, port + 1))
        self.socket_recorders.append(socket_optitrack_recorder)    

    def init_emg(self):
        parameters = EMGHandler.get_parameters()
        ip = parameters["streaming_ip"]
        port = parameters["port"]

        context = zmq.Context()
        self.socket_emg = context.socket(zmq.SUB)
        self.socket_emg.connect("tcp://%s:%s" % (ip, port))
        self.socket_emg.setsockopt(zmq.SUBSCRIBE, b'emg')

        context = zmq.Context()
        socket_emg_recorder = context.socket(zmq.REQ)
        socket_emg_recorder.connect("tcp://%s:%s" % (ip, port + 1))
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

    def get_optitrack_data(self):
        while not self.stop_event.is_set():
            data = OptitrackHandler.receive_data(self.socket_opt)
            self.opt_data.append(data['optitrack'])

    def get_buffered(self, data, header):
        if data:
            return pd.DataFrame(data=np.array(data)[:,1:], index=np.array(data)[:,0], columns=header[1:])
        return pd.DataFrame(columns=header[1:])

    def get_buffered_emg(self):
        header = ["index", "absolute_time", "relative_time"] + EMGHandler.get_parameters()["header"]
        return self.get_buffered(self.emg_data, header)

    def get_buffered_opt(self):
        header = ["index", "absolute_time", "relative_time"] + OptitrackHandler.get_parameters()["header"]
        return self.get_buffered(self.opt_data, header)

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