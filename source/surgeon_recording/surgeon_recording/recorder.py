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
from surgeon_recording.sensor_handlers.camera_handler import CameraHandler
from surgeon_recording.sensor_handlers.emg_handler import EMGHandler
from surgeon_recording.sensor_handlers.optitrack_handler import OptitrackHandler
from surgeon_recording.sensor_handlers.tps_handler import TPSHandler

class Recorder(object):
    def __init__(self, data_folder):
        self.recording = False
        self.data_folder = data_folder
        self.exp_folder = ""

        # init data storage
        self.data = {}
        self.buffered_images = {}
        self.init_data_buffer()

        # init all sensors
        self.sensor_list = ["camera", "optitrack", "emg", "tps"]
        self.sensor_sockets = {}
        self.recorder_sockets = {}

        self.topics = {}
        self.topics["camera"] = ["rgb", "depth"]
        self.topics["optitrack"] = ["optitrack"]
        self.topics["emg"] = ["emg"]
        self.topics["tps"] = ["tps"]

        self.parameters = {}
        self.parameters["camera"] = CameraHandler.get_parameters()
        self.parameters["optitrack"] = OptitrackHandler.get_parameters()
        self.parameters["emg"] = EMGHandler.get_parameters()
        self.parameters["tps"] = TPSHandler.get_parameters()

        for s in self.sensor_list:
            self.init_sensor(s)

        # initiliaze the threads
        self.stop_event = Event()
        self.recording_threads = []
        self.recording_threads.append(Thread(target=self.get_camera_data))
        self.recording_threads.append(Thread(target=self.get_emg_data))
        self.recording_threads.append(Thread(target=self.get_optitrack_data))
        self.recording_threads.append(Thread(target=self.get_tps_data))

        for t in self.recording_threads:
            t.start()

    def init_data_buffer(self):
        self.data["emg"] = deque(maxlen=2000)
        self.data["optitrack"] = deque(maxlen=100)
        self.data["tps"] = deque(maxlen=100)

    def init_recording_folder(self, folder):
        self.exp_folder = join(self.data_folder, folder)
        if not os.path.exists(self.exp_folder):
            os.makedirs(self.exp_folder)    

    def init_sensor(self, sensor_name):
        ip = self.parameters[sensor_name]["streaming_ip"] if self.parameters[sensor_name]["streaming_ip"] != "*" else "127.0.0.1"
        port = self.parameters[sensor_name]["streaming_port"]

        context = zmq.Context()
        self.sensor_sockets[sensor_name] = context.socket(zmq.SUB)
        for t in self.topics[sensor_name]:
            self.sensor_sockets[sensor_name].subscribe(str.encode(t))
        self.sensor_sockets[sensor_name].setsockopt(zmq.SNDHWM, 10)
        self.sensor_sockets[sensor_name].setsockopt(zmq.SNDBUF, 10*1024)
        self.sensor_sockets[sensor_name].connect("tcp://%s:%s" % (ip, port))

        context = zmq.Context()
        socket_recorder = context.socket(zmq.REQ)
        socket_recorder.connect("tcp://%s:%s" % (ip, port + 1))
        self.recorder_sockets[sensor_name] = socket_recorder

    def get_camera_data(self):
        while not self.stop_event.is_set():
            data = CameraHandler.receive_data(self.sensor_sockets["camera"])
            self.buffered_images.update(data)

    def get_emg_data(self):
        while not self.stop_event.is_set():
            signal = EMGHandler.receive_data(self.sensor_sockets["emg"])
            for s in signal[self.topics["emg"][0]]:
                self.data["emg"].append(s)

    def get_optitrack_data(self):
        while not self.stop_event.is_set():
            data = OptitrackHandler.receive_data(self.sensor_sockets["optitrack"])
            self.data["optitrack"].append(data[self.topics["optitrack"][0]])

    def get_tps_data(self):
        while not self.stop_event.is_set():
            data = TPSHandler.receive_data(self.sensor_sockets["tps"])
            self.data["tps"].append(data[self.topics["tps"][0]])

    def get_buffered_data(self, sensor_name):
        header = ["index", "absolute_time", "relative_time"] + self.parameters[sensor_name]["header"]
        data = self.data[sensor_name]
        if data:
            return pd.DataFrame(data=np.array(data)[:,1:], index=np.array(data)[:,0], columns=header[1:])
        return pd.DataFrame(columns=header[1:])

    def get_buffered_rgb(self):
        return cv2.imencode('.jpg', self.buffered_images['rgb'])[1]

    def get_buffered_depth(self):
        return cv2.imencode('.jpg', self.buffered_images['depth'])[1]

    def record(self, folder):
        self.recording = True
        self.init_recording_folder(folder)
        self.init_data_buffer()
        message = {'recording': True, 'folder': os.path.abspath(self.exp_folder), 'start_time': time.time()}
        for key, s in self.recorder_sockets.items():
            s.send_json(message)
            s.recv_string()
    
    def stop_recording(self):
        self.recording = False
        message = {'recording': False}
        for key, s in self.recorder_sockets.items():
            s.send_json(message)
            s.recv_string()

    def shutdown(self):
        self.stop_event.set()
        for s in self.sensor_list:
            self.sensor_sockets[s].close()
            self.recorder_sockets[s].close()
