import numpy as np
import zmq
import csv
from threading import Thread, Event, Lock
import os
from os.path import join
import time
import json

class SensorHandler(object):
    def __init__(self, sensor_name, parameters):
        self.sensor_name = sensor_name
        self.header = parameters["header"]
        ip = parameters["streaming_ip"]
        port = parameters["streaming_port"]

        self.recording = False
        self.index = 0
        self.start_time = time.time()
        self.timestep = 0.001 # security to not overfload the network
        
        # socket for publisher
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.SNDHWM, 10)
        self.socket.setsockopt(zmq.SNDBUF, 10*1024)
        self.socket.bind("tcp://%s:%s" % (ip, port))
        # socker for recorder server
        self.recorder_socket = context.socket(zmq.REP)
        self.recorder_socket.bind("tcp://%s:%s" % (ip, port + 1))
        self.recorder_socket.setsockopt(zmq.LINGER, 0)

        self.stop_event = Event()
        self.recording_thread = Thread(target=self.recording_request_handler)
        self.recording_thread.start()
        self.lock = Lock()

    @staticmethod
    def read_config_file():
        filepath = os.path.abspath(os.path.dirname(__file__))
        with open(join(filepath, '..', '..', 'config', 'sensor_parameters.json'), 'r') as paramfile:
            return json.load(paramfile)

    def generate_fake_data(self, dim, mean=0., var=1.):
        return np.random.normal(size=dim, loc=mean, scale=var)

    def acquire_data(self):
        return []

    def send_data(self, topic, data):
        if len(data) > 0:
            self.socket.send_string(topic, zmq.SNDMORE)
            self.socket.send_pyobj(data)

    @staticmethod
    def receive_data(socket):
        topic = socket.recv_string()
        data = socket.recv_pyobj()
        return {topic: data}

    def recording_request_handler(self):
        while not self.stop_event.wait(0.01):
            print('Waiting for commands')
            message = self.recorder_socket.recv_json()
            if message['recording'] and not self.recording:
                self.setup_recording(message['folder'], message['start_time'])
                self.recorder_socket.send_string("recording started")
                print('Recording started')
            elif not message['recording'] and self.recording:
                self.stop_recording()
                self.recorder_socket.send_string("recording stopped")
                print('Recording stopped')
            else:
                self.recorder_socket.send_string("recording" if self.recording else "not recording")

    def setup_recording(self, recording_folder, start_time):
        with self.lock:
            if not os.path.exists(recording_folder):
                os.makedirs(recording_folder)

            f = open(join(recording_folder, self.sensor_name + '.csv'), 'w', newline='')
            self.writer = {"file": f, "writer": csv.writer(f)}
            self.writer["writer"].writerow(["index", "absolute_time", "relative_time"] + self.header)

            self.index = 0
            self.start_time = start_time
            self.recording = True

    def stop_recording(self):
        with self.lock:
            self.recording = False
            self.writer['file'].close()

    def record(self, data):
        if self.recording:
            if data:
                if isinstance(data[0], list):
                    for d in data:
                        self.writer["writer"].writerow(d)
                else:
                    self.writer["writer"].writerow(data)

    def shutdown(self):
        self.stop_event.set()
        self.socket.close()
        self.recorder_socket.close()
        self.recording_thread.join()

    def run(self):
        while True:
            try:
                start = time.time()
                with self.lock:
                    data = self.acquire_data()
                    self.record(data)
                    self.send_data(self.sensor_name, data)
                effective_time = time.time() - start
                wait_period = self.timestep - effective_time
                if wait_period > 0:
                    time.sleep(wait_period)
            except KeyboardInterrupt:
                print('Interruption, shutting down')
                break
        self.shutdown()
