import plotly.graph_objects as go


from os.path import join
import cv2
import base64
import time
import pyrealsense2 as rs
import numpy as np

from surgeon_recording.data_analysis.analyser import Analyser


if __name__ == '__main__':
	# example ; graph_choice = [ 'x', tps', 'emg']
	graph_choice = [ 'tps', 'emg']
	data_files =   ['cut'+ str(i+1) for i in range(19) ]
	data_files1 =  ['cut'+ str(i+21) for i in range(10) ]
	data_files2 =  ['cut'+ str(i+31) for i in range(10) ]
	data_folder = 'data'
	dtw=False
    
	plot_bool = False
	sigma = [4,3,2]
	nb_interpolation_pts=5000


	analyse = Analyser()


	data_files3=['cut10']
	

	#analyse.compute_cinematics(data_folder, coordinates, data_files, plot_bool, sigma )

	analyse.plot_analysis(data_folder, graph_choice, data_files, dtw, sigma, nb_interpolation_pts)

	#analyse.emg_test_filter( data_folder, data_files3, index )

	#analyse.emg_plot_only( data_folder, data_files, dtw, nb_interpolation_pts )

	#analyse.plot_analysis(data_folder, coordinates, data_files1, dtw)

	#analyse.plot_analysis(data_folder, coordinates, data_files2, dtw)

