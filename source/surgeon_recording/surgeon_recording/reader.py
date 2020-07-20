import sys
from os.path import join
import pandas as pd
import numpy as np
import cv2
from multiprocessing import Lock


class Reader(object):
	def __init__(self):
		self.camera_data = []
		self.opt_data = []
		self.emg_data = []
		self.video = {}
		self.current_image = {}
		self.camera_frame_index = 0
		self.opt_frame_index = 0
		self.emg_frame_index = 0
		self.start_opt_frame = 0
		self.stop_opt_frame = 1000000
		self.start_emg_frame = 0
		self.stop_emg_frame = 1000000
		self.opt_rate = 2
		self.emg_rate = 35
		self.mutex = Lock()

	def get_indexes(self, camera_index):
		max_index = self.camera_data.count()[0]
		if camera_index < 0 or camera_index > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(camera_index))
			return -1
		camera_frame = self.camera_data.iloc[camera_index]
		time = camera_frame[0]
		# extract the opt data
		opt_index = int(camera_index * self.opt_rate)
		opt_frame = self.opt_data.iloc[opt_index]
		while abs(time - opt_frame[0]) < 1e-2:
			opt_index = opt_index + 1
			opt_frame = self.opt_data.iloc[opt_index]
		# extract the emg data
		emg_index = int(camera_index * self.emg_rate)
		emg_frame = self.emg_data.iloc[emg_index]
		while abs(time - emg_frame[0]) < 1e-2:
			emg_index = emg_index + 1
			emg_frame = self.emg_data.iloc[emg_index]
		return opt_index, emg_index

	def get_data(self, start_frame, stop_frame):
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

	def get_emg(self, camera_index, window_width=1000):
		max_index = self.camera_data.count()[0]
		if camera_index < 0 or camera_index > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(camera_index))
			return -1
		camera_frame = self.camera_data.iloc[camera_index]
		time = camera_frame[0]
		# extract the opt data
		emg_index = int(camera_index * self.emg_rate)
		emg_frame = self.emg_data.iloc[emg_index]
		while abs(time - emg_frame[0]) < 1e-2:
			emg_index = emg_index + 1
			emg_frame = self.emg_data.iloc[emg_index]
		start_index = max(emg_index - window_width, 0)
		end_index = min(emg_index + window_width, self.emg_data.count()[0])
		emg_frame =  self.emg_data.iloc[start_index:end_index]
		return emg_index, emg_frame

	def get_opt(self, camera_index, window_width=50):
		max_index = self.camera_data.count()[0]
		if camera_index < 0 or camera_index > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(i))
			return -1
		camera_frame = self.camera_data.iloc[i]
		time = camera_frame[0]
		# extract the opt data
		opt_index = int(camera_index * self.opt_rate)
		opt_frame = self.opt_data.iloc[opt_index]
		while abs(time - opt_frame[0]) < 1e-2:
			opt_index = opt_index + 1
			opt_frame = self.opt_data.iloc[opt_index]
		start_index = max(opt_index - window_width, 0)
		end_index = min(opt_index + window_width, self.opt_data.count()[0])
		opt_frame =  self.opt_data.iloc[start_index:end_index]
		return opt_index, opt_frame

	def get_nb_frames(self):
		return self.camera_data.count()[0]

	def set_starting_image(self, video_type, desired_frame):
		max_index = self.camera_data.count()[0]
		if desired_frame < 0 or desired_frame > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(desired_frame))
			return -1

		with self.mutex:
			self.video[video_type] = cv2.VideoCapture(join(self.exp_folder, video_type + ".avi"))
			for i in range(desired_frame + 1):
				_, frame = self.video[video_type].read()
			_, self.current_image[video_type] = cv2.imencode('.jpg', frame)

	def get_image(self, video_type, desired_frame):
		max_index = self.camera_data.count()[0]
		if desired_frame < 0 or desired_frame > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(desired_frame))
			return -1

		with self.mutex:
			self.video[video_type] = cv2.VideoCapture(join(self.exp_folder, video_type + ".avi"))
			for i in range(desired_frame + 1):
				_, frame = self.video[video_type].read()

			_, buffer = cv2.imencode('.jpg', frame)
		return buffer

	def get_image(self, video_type):
		return self.current_image[video_type]

	def get_next_images(self):
		with self.mutex:
			for t in ["rgb", "depth"]:
				_, frame = self.video[t].read()
				_, self.current_image[t] = cv2.imencode('.jpg', frame)

	def play(self, exp_folder):
		self.exp_folder = exp_folder
		with self.mutex:
			self.video["rgb"] = cv2.VideoCapture(join(self.exp_folder, "rgb.avi"))
			self.video["depth"] = cv2.VideoCapture(join(self.exp_folder, "depth.avi"))
		self.get_next_images()
		self.camera_data = pd.read_csv(join(exp_folder, "camera.csv")).set_index('index')
		self.opt_data = pd.read_csv(join(exp_folder, "opt.csv")).set_index('index')
		self.emg_data = pd.read_csv(join(exp_folder, "emg.csv")).set_index('index')