import plotly.graph_objects as go


from os.path import join
import cv2
import base64
import time
import pyrealsense2 as rs
import numpy as np

from surgeon_recording.data_analysis.analyser import Analyser


if __name__ == '__main__':

	coordinates = ['x','y','z']
	data_files =   ['cut'+ str(i+1) for i in range(10) ]
	data_files1 =  ['cut'+ str(i+21) for i in range(10) ]
	data_files2 =  ['cut'+ str(i+31) for i in range(10) ]
	data_folder = 'data'
	dtw=True
	plot_bool=False

	analyse = Analyser()

	analyse.compute_cinematics(data_folder, coordinates, data_files, plot_bool)

	analyse.plot_analysis(data_folder, coordinates, data_files, dtw)

	#analyse.plot_analysis(data_folder, coordinates, data_files1, dtw)

	#analyse.plot_analysis(data_folder, coordinates, data_files2, dtw)

