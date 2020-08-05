import sys
from os.path import join
import pandas as pd
import numpy as np
import cv2
from threading import Thread, Event
from multiprocessing import Lock
import os
import asyncio
import time
from surgeon_recording.sensor_handlers.camera_handler import CameraHandler


class Reader(object):
    def __init__(self):
        self.sensor_list = ["camera", "emg", "optitrack", "tps"]
        self.data = {}
        self.images = {}
        self.frame_indexes = {}
        self.start_frames = {}
        self.stop_frames = {}
        self.sensor_rates = {}
        for s in self.sensor_list:
            self.data[s] = []
            self.frame_indexes[s] = 0
            self.start_frames[s] = 0
            self.stop_frames[s] = 1000000
        self.mutex = Lock()
        self.blank_image = CameraHandler.create_blank_image(encode=True)
        self.data_changed = False
        self.stop_event = Event()
        self.image_extractor_thread = Thread(target=self.extract_images)
        self.image_extractor_thread.daemon = True
        self.image_extractor_thread.start()

    def initialize_sensor_rate(self, sensor):
        self.sensor_rates[sensor] = self.get_nb_sensor_frames(sensor) / self.get_nb_frames()

    def get_experiment_list(self, data_folder):
        res = {}
        needed_files = [s + '.csv' for s in self.sensor_list] + ['rgb.avi', 'depth.avi']
        exp_list = []
        exp_list = [x[0] for x in os.walk(data_folder) if all(item in x[2] for item in needed_files)]
        for exp in exp_list:
            res[exp] = exp
        return res

    def get_indexes(self, camera_index):
        max_index = self.get_nb_frames()
        if camera_index < 0 or camera_index > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(camera_index))
            return -1
        camera_frame = self.data["camera"].iloc[camera_index]
        time = camera_frame[1]
        # extract the other sensor data (exept camera)
        indexes = {}
        for s in self.sensor_list[1:]:
            index = int(camera_index * self.sensor_rates[s])
            frame = self.data[s].iloc[index]
            indexes[s] = index
            while abs(time - frame[1]) > 1e-3 and index <= (self.get_nb_sensor_frames(s) - 2) and index >= 1:
                sign = np.sign(time - frame[1])
                index = int(index + sign * 1)
                frame = self.data[s].iloc[index]
                indexes[s] = index
        return indexes

    def get_window_data(self, start_frame, stop_frame):
        max_index = self.get_nb_frames()
        if start_frame < 0 or start_frame > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(start_frame))
            return -1
        if stop_frame < 0 or stop_frame > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(stop_frame))
            return -1
        start_indexes = self.get_indexes(start_frame)
        stop_indexes = self.get_indexes(stop_frame)
        window_data = {}
        for s in self.sensor_list[1:]:
            window_data[s] = self.data[s].iloc[start_indexes[s]:stop_indexes[s]+1]
        return window_data

    def set_starting_frame(self, start_frame):
        max_index = self.get_nb_frames()
        if start_frame < 0 or start_frame > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(start_frame))
            return -1
        self.start_frames = self.get_indexes(start_frame)

    def set_stopping_frame(self, stop_frame):
        max_index = self.get_nb_frames()
        if stop_frame < 0 or stop_frame > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(stop_frame))
            return -1
        self.stop_frames = self.get_indexes(stop_frame)

    def get_data(self):
        window_data = {}
        for s in self.sensor_list:
            window_data[s] = self.data[s].iloc[self.start_frames[s]:self.stopt_frames[s]]
        return window_data

    def get_nb_frames(self):
        return self.data["camera"].count()[0]

    def get_nb_sensor_frames(self, sensor):
        return self.data[sensor].count()[0]

    def init_image_list(self):
        for t in ["rgb", "depth"]:
            self.images[t] = []
            for i in range(len(self.data["camera"])):
                with self.mutex:
                    self.images[t].append(self.blank_image)

    def extract_image(self, video):
        _, frame = video.read()
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer

    def extract_images(self):
        while True:
            if self.data_changed:
                self.data_changed = False
                rgb_video = cv2.VideoCapture(join(self.exp_folder, "rgb.avi"))
                depth_video = cv2.VideoCapture(join(self.exp_folder, "depth.avi"))
                for i in range(self.get_nb_frames()):
                    if self.data_changed:
                        break
                    rgb_image = self.extract_image(rgb_video)
                    depth_image = self.extract_image(depth_video)
                    with self.mutex:
                        self.images["rgb"][i] = rgb_image
                        self.images["depth"][i] = depth_image
                rgb_video.release()
                depth_video.release()
            time.sleep(0.01)

    def get_image(self, video_type, frame_index):
        max_index = self.get_nb_frames()
        if frame_index < 0 or frame_index > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(frame_index))
            return -1
        with self.mutex:
            image = self.images[video_type][frame_index]
        return image

    def play(self, exp_folder):
        self.exp_folder = exp_folder
        for s in self.sensor_list:
            self.data[s] = pd.read_csv(join(exp_folder, s + ".csv")).set_index('index')
            self.initialize_sensor_rate(s)
        self.init_image_list()
        self.data_changed = True
        
    def export(self, folder, start_index, stop_index):
        export_folder = join(self.exp_folder, folder)
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        cut_camera_data = self.data["camera"].iloc[start_index:stop_index+1]
        cut_camera_data.to_csv(join(export_folder, 'camera.csv'))
        print("Camera data file exported")
        cut_data = self.get_window_data(start_index, stop_index)
        for key, value in cut_data.items():
            value.to_csv(join(export_folder, key + '.csv'))
            print(key + " data file exported")
        self.export_video(export_folder, start_index, stop_index)
        print("Export complete")

    def export_video(self, folder, start_index, stop_index):
        for t in ["rgb", "depth"]:
            original_video = cv2.VideoCapture(join(self.exp_folder, t + '.avi'))
            cut_video = cv2.VideoWriter(join(folder, t + '.avi'), cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
            for i in range(stop_index + 1):
                _, frame = original_video.read()
                if i < start_index:
                    continue
                cut_video.write(frame)
            print(t + " video file exported")
            original_video.release()
            cut_video.release()