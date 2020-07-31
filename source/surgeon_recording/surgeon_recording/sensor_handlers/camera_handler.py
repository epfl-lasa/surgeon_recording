import pyrealsense2 as rs
import numpy as np
import zmq
import cv2
import csv
import os
from os.path import join
import time
from surgeon_recording.sensor_handlers.sensor_handler import SensorHandler

class CameraHandler(SensorHandler):
    def __init__(self, parameters):
        SensorHandler.__init__(self, 'camera', parameters)
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.color_image = []
        self.depth_colormap = []
        self.recording = False

        try:
            self.pipeline.start(self.config)
        except:
            print("Error initializing the camera")

    @staticmethod
    def get_parameters():
        parameters = SensorHandler.read_config_file()
        param = parameters['camera']
        param.update({ 'header': [] })
        return param

    def acquire_data(self):
        # Wait for a coherent pair of frames: depth and color
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            return

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        self.color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        self.depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        absolute_time = time.time()
        data = [self.index + 1, absolute_time, absolute_time - self.start_time]
        self.index = data[0]
        return data

    def send_data(self, topic, data):
        super().send_data(topic, data)
        super().send_data('rgb', self.color_image)
        super().send_data('depth', self.depth_colormap)

    @staticmethod
    def display_images(color_image, depth_image):
        # Stack both images horizontally
        images = np.hstack((color_image, depth_image))
        # # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        cv2.waitKey(1)

    def setup_recording(self, recording_folder, start_time):
        super().setup_recording(recording_folder, start_time)
        with self.lock:
            color_path = join(recording_folder, 'rgb.avi')
            depth_path = join(recording_folder, 'depth.avi')
            self.colorwriter = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
            self.depthwriter = cv2.VideoWriter(depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)

    def stop_recording(self):
        super().stop_recording()
        with self.lock:
            self.colorwriter.release()
            self.depthwriter.release()

    def record(self, data):
        super().record(data)
        if self.recording:
            with self.lock:
                # write the images
                self.colorwriter.write(self.color_image)
                self.depthwriter.write(self.depth_colormap)

    def shutdown(self):
        super().shutdown()
        self.pipeline.stop()


def main(args=None):
    parameters = CameraHandler.get_parameters()
    camera_handler = CameraHandler(parameters)
    camera_handler.run()
    
if __name__ == '__main__':
    main()