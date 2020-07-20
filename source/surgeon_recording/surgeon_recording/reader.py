import sys
from os.path import join
import pandas as pd
import numpy as np
import cv2


class Reader(object):
	def __init__(self):
		self.camera_data = []
		self.opt_data = []
		self.emg_data = []
		self.camera_frame_index = 0
		self.opt_frame_index = 0
		self.emg_frame_index = 0

	def get_indexes(self, camera_index):
		max_index = self.camera_data.count()[0]
		if camera_index < 0 or camera_index > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(camera_index))
			return -1
		camera_frame = self.camera_data.iloc[camera_index]
		time = camera_frame[0]
		# extract the opt data
		opt_index = 0
		opt_frame = self.opt_data.iloc[opt_index]
		while opt_frame[0] < time:
			opt_index = opt_index + 1
			opt_frame = self.opt_data.iloc[opt_index]
		# extract the emg data
		emg_index = 0
		emg_frame = self.emg_data.iloc[emg_index]
		while emg_frame[0] < time:
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

	def get_frame(self, i, window_width=50):
		max_index = self.camera_data.count()[0]
		if i < 0 or i > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(i))
			return -1
		camera_frame = self.camera_data.iloc[i]
		time = camera_frame[0]
		# extract the opt data
		j = 0
		opt_frame = self.opt_data.iloc[j]
		while opt_frame[0] < time:
			j = j + 1
			opt_frame = self.opt_data.iloc[j]
		start_index = max(j - window_width, 0)
		end_index = min(j + window_width, self.opt_data.count()[0])
		opt_frame =  self.opt_data.iloc[start_index:end_index]
		# extract the emg data
		j = 0
		emg_frame = self.emg_data.iloc[j]
		while emg_frame[0] < time:
			j = j + 1
			emg_frame = self.emg_data.iloc[j]
		start_index = max(j - window_width, 0)
		end_index = min(j + window_width, self.emg_data.count()[0])
		emg_frame =  self.emg_data.iloc[start_index:end_index]
		return opt_frame, emg_frame

	def set_current_frame(self, i, window_width=50):
		max_index = self.camera_data.count()[0]
		if i < 0 or i > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(i))
			return -1
		self.camera_frame_index = i
		camera_frame = self.camera_data.iloc[i]
		time = camera_frame[0]
		# extract the opt data
		j = 0
		opt_frame = self.opt_data.iloc[j]
		while opt_frame[0] < time:
			j = j + 1
			opt_frame = self.opt_data.iloc[j]
		start_index = max(j - window_width, 0)
		end_index = min(j + window_width, self.opt_data.count()[0])
		opt_frame =  self.opt_data.iloc[start_index:end_index]
		self.opt_frame_index = j
		# extract the emg data
		j = 0
		emg_frame = self.emg_data.iloc[j]
		while emg_frame[0] < time:
			j = j + 1
			emg_frame = self.emg_data.iloc[j]
		start_index = max(j - window_width, 0)
		end_index = min(j + window_width, self.emg_data.count()[0])
		emg_frame =  self.emg_data.iloc[start_index:end_index]
		self.emg_frame_index = j
		return opt_frame, emg_frame

	def get_current_frame(self, window_width=50):
		camera_frame = self.camera_data.iloc[self.camera_frame_index]
		start_index = max(self.opt_frame_index - window_width, 0)
		end_index = min(self.opt_frame_index + window_width, self.opt_data.count()[0])
		opt_frame =  self.opt_data.iloc[start_index:end_index]
		start_index = max(self.emg_frame_index - window_width, 0)
		end_index = min(self.emg_frame_index + window_width, self.emg_data.count()[0])
		emg_frame =  self.emg_data.iloc[start_index:end_index]
		return opt_frame, emg_frame

	def get_next_frame(self, offset=1, window_width=50):
		i = self.camera_frame_index + offset
		max_index = self.camera_data.count()[0]
		if i < 0 or i > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(i))
			return -1
		self.camera_frame_index = i
		camera_frame = self.camera_data.iloc[i]
		time = camera_frame[0]
		# extract the opt data
		j = self.opt_frame_index
		opt_frame = self.opt_data.iloc[j]
		while opt_frame[0] < time:
			j = j + 1
			opt_frame = self.opt_data.iloc[j]
		start_index = max(j - window_width, 0)
		end_index = min(j + window_width, self.opt_data.count()[0])
		opt_frame =  self.opt_data.iloc[start_index:end_index]
		self.opt_frame_index = j
		# extract the emg data
		j = self.emg_frame_index
		emg_frame = self.emg_data.iloc[j]
		while emg_frame[0] < time:
			j = j + 1
			emg_frame = self.emg_data.iloc[j]
		start_index = max(j - window_width, 0)
		end_index = min(j + window_width, self.emg_data.count()[0])
		emg_frame =  self.emg_data.iloc[start_index:end_index]
		self.emg_frame_index = j
		return opt_frame, emg_frame

	def get_previous_frame(self, offset=0, window_width=50):
		i = self.camera_frame_index - offset
		max_index = self.camera_data.count()[0]
		if i < 0 or i > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(i))
			return -1
		self.camera_frame_index = i
		camera_frame = self.camera_data.iloc[i]
		time = camera_frame[0]
		# extract the opt data
		j = self.opt_frame_index
		opt_frame = self.opt_data.iloc[j]
		while opt_frame[0] > time:
			j = j - 1
			opt_frame = self.opt_data.iloc[j]
		start_index = max(j - window_width, 0)
		end_index = min(j + window_width, self.opt_data.count()[0])
		opt_frame =  self.opt_data.iloc[start_index:end_index]
		self.opt_frame_index = j
		# extract the emg data
		j = self.emg_frame_index
		emg_frame = self.emg_data.iloc[j]
		while emg_frame[0] > time:
			j = j - 1
			emg_frame = self.emg_data.iloc[j]
		start_index = max(j - window_width, 0)
		end_index = min(j + window_width, self.emg_data.count()[0])
		emg_frame =  self.emg_data.iloc[start_index:end_index]
		self.emg_frame_index = j
		return opt_frame, emg_frame

	def get_nb_frames(self):
		return self.camera_data.count()[0]

	def get_image(self, video_type, desired_frame):
		max_index = self.camera_data.count()[0]
		if desired_frame < 0 or desired_frame > max_index:
			print("Incorrect index, expected number between 0 and " + str(max_index) + " got " + str(desired_frame))
			return -1

		video = cv2.VideoCapture(join(self.exp_folder, video_type + ".avi"))
		for i in range(desired_frame + 1):
			_, frame = video.read()

		_, buffer = cv2.imencode('.jpg', frame)
		video.release()
		return buffer

	def play(self, exp_folder):
		self.exp_folder = exp_folder
		self.camera_data = pd.read_csv(join(exp_folder, "camera.csv")).set_index('index')
		self.opt_data = pd.read_csv(join(exp_folder, "opt.csv")).set_index('index')
		self.emg_data = pd.read_csv(join(exp_folder, "emg.csv")).set_index('index')