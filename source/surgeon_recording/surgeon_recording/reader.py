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
from surgeon_recording.sensor_handlers.camera_handler.CameraHandler import create_blank_image


class Reader(object):
    def __init__(self):
        self.camera_data = []
        self.opt_data = []
        self.emg_data = []
        self.images = {}
        self.camera_frame_index = 0
        self.opt_frame_index = 0
        self.emg_frame_index = 0
        self.start_opt_frame = 0
        self.stop_opt_frame = 1000000
        self.start_emg_frame = 0
        self.stop_emg_frame = 1000000
        self.mutex = Lock()
        self.blank_image = self.create_blank_image(encode=True)
        self.data_changed = False
        self.stop_event = Event()
        self.image_extractor_thread = Thread(target=self.extract_images)
        self.image_extractor_thread.daemon = True
        self.image_extractor_thread.start()

    def initialize_sensor_rates(self):
        self.opt_rate = self.get_nb_opt_frames / self.get_nb_frames
        self.emg_rate = self.get_nb_emg_frames / self.get_nb_frames

    def get_experiment_list(self, data_folder):
        res = {}
        needed_files = ['emg.csv', 'optitrack.csv', 'rgb.avi', 'depth.avi', 'camera.csv']
        exp_list = []
        exp_list = [x[0] for x in os.walk(data_folder) if all(item in x[2] for item in needed_files)]
        for exp in exp_list:
            res[exp] = exp
        return res

    def get_indexes(self, camera_index):
        max_index = self.camera_data.count()[0]
        if camera_index < 0 or camera_index > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(camera_index))
            return -1
        camera_frame = self.camera_data.iloc[camera_index]
        time = camera_frame[1]
        # extract the opt data
        opt_index = int(camera_index * self.opt_rate)
        opt_frame = self.opt_data.iloc[opt_index]
        while abs(time - opt_frame[1]) > 1e-2 and opt_index <= (self.opt_data.count()[0] - 2) and opt_index >= 1:
            sign = np.sign(time - opt_frame[1])
            opt_index = int(opt_index + sign * 1)
            opt_frame = self.opt_data.iloc[opt_index]
        # extract the emg data
        emg_index = int(camera_index * self.emg_rate)
        emg_frame = self.emg_data.iloc[emg_index]
        while abs(time - emg_frame[1]) > 1e-2 and opt_index <= (self.emg_data.count()[0] - 2) and emg_index >= 1:
            sign = np.sign(time - emg_frame[1])
            emg_index = int(emg_index + sign * 1)
            emg_frame = self.emg_data.iloc[emg_index]
        return opt_index, emg_index

    def get_window_data(self, start_frame, stop_frame):
        max_index = self.camera_data.count()[0]
        if start_frame < 0 or start_frame > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(start_frame))
            return -1
        if stop_frame < 0 or stop_frame > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(stop_frame))
            return -1
        opt_start, emg_start = self.get_indexes(start_frame)
        opt_stop, emg_stop = self.get_indexes(stop_frame)
        return self.opt_data.iloc[opt_start:opt_stop], self.emg_data.iloc[emg_start:emg_stop]

    def set_starting_frame(self, start_frame):
        max_index = self.camera_data.count()[0]
        if start_frame < 0 or start_frame > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(start_frame))
            return -1
        self.start_opt_frame, self.start_emg_frame = self.get_indexes(start_frame)

    def set_stopping_frame(self, stop_frame):
        max_index = self.camera_data.count()[0]
        if stop_frame < 0 or stop_frame > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(stop_frame))
            return -1
        self.stop_opt_frame, self.stop_emg_frame = self.get_indexes(stop_frame)

    def get_data(self):
        return self.opt_data.iloc[self.start_opt_frame:self.stop_opt_frame], self.emg_data.iloc[self.start_emg_frame:self.stop_emg_frame]

    def get_nb_frames(self):
        return self.camera_data.count()[0]

    def get_nb_emg_frames(self):
        return self.emg_data.count()[0]

    def init_image_list(self):
        for t in ["rgb", "depth"]:
            self.images[t] = []
            for i in range(len(self.camera_data)):
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
        max_index = self.camera_data.count()[0]
        if frame_index < 0 or frame_index > max_index:
            print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(frame_index))
            return -1
        with self.mutex:
            image = self.images[video_type][frame_index]
        return image

    def play(self, exp_folder):
        self.exp_folder = exp_folder
        self.camera_data = pd.read_csv(join(exp_folder, "camera.csv")).set_index('index')
        self.opt_data = pd.read_csv(join(exp_folder, "optitrack.csv")).set_index('index')
        self.emg_data = pd.read_csv(join(exp_folder, "emg.csv")).set_index('index')
        self.init_image_list()
        self.data_changed = True
        
    def export(self, folder, start_index, stop_index):
        export_folder = join(self.exp_folder, folder)
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        cut_camera_data = self.camera_data.iloc[start_index:stop_index]
        cut_camera_data.to_csv(join(export_folder, 'camera.csv'))
        print("Camera data file exported")
        cut_opt_data, cut_emg_data = self.get_window_data(start_index, stop_index)
        cut_opt_data.to_csv(join(export_folder, 'optitrack.csv'))
        print("Optitrack data file exported")
        cut_emg_data.to_csv(join(export_folder, 'emg.csv'))
        print("EMG data file exported")
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