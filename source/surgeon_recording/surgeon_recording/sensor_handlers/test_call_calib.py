
from importlib.abc import ResourceReader
import numpy as np
import zmq
import csv
from threading import Thread, Event, Lock
import os
from os.path import join
import time
import json
import keyboard
import subprocess
from shutil import copyfile


from surgeon_recording.sensor_handlers.tps_calib import TPScalibration

folder_input = "6"
subject_input = "6"
folder = join("/Users/LASA/Documents/Recordings/surgeon_recording/exp_data", folder_input, subject_input)


       
csv_path_tps_raw = join(folder, "TPS_recording_raw.csv")
csv_path_tps_cal = join(folder, "TPS_calibrated.csv")



calib_tps = TPScalibration(csv_path = csv_path_tps_cal, folder_input = folder_input, subject_nb=subject_input, csv_raw_data=csv_path_tps_raw)
#calib_tps = TPScalibration(csv_path_tps_cal, folder_input, subject_input, csv_path_tps_raw)
