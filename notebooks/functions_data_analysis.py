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
from shutil import copyfile
from surgeon_recording.sensor_handlers.camera_handler import CameraHandler
from os.path import exists
from bisect import bisect_left

import csv
from natsort import natsorted

from moviepy.editor import *
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

class data_analysis(object):
    
    """
    A class used to define functions for synchronization of 3 videos (RS, GOPRO, MICROSCOPE) and sensor data
    
    """
    
    def __init__(self):
        
        
        
        
    def processed_emg_data