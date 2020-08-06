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
        self.simulate = parameters["simulate"]
        self.color_image = []
        self.depth_colormap = []
        if not self.simulate:
            self.pipeline = rs.pipeline()
            self.config = rs.config()
            self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            try:
                self.pipeline.start(self.config)
            except:
                print("Error initializing the camera")
        self.colorwriter = None
        self.depthwriter = None

    @staticmethod
    def get_parameters():
        parameters = SensorHandler.read_config_file()
        param = parameters['camera']
        param.update({ 'header': [] })
        return param

    @staticmethod
    def create_blank_image(encode=False):
        image = np.zeros((480, 640, 3), np.uint8)
        # Since OpenCV uses BGR, convert the color first
        color = tuple((0, 0, 0))
        # Fill image with color
        image[:] = color
        if not encode:
            return image
        return cv2.imencode('.jpg', image)[1]

    def acquire_data(self):
        if not self.simulate:
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
        else:
            self.color_image = CameraHandler.create_blank_image()
            self.depth_colormap = CameraHandler.create_blank_image()
            time.sleep(0.03)

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
        with self.lock:
            color_path = join(recording_folder, 'rgb.avi')
            depth_path = join(recording_folder, 'depth.avi')
            self.colorwriter = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
            self.depthwriter = cv2.VideoWriter(depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
        super().setup_recording(recording_folder, start_time)

    def stop_recording(self):
        super().stop_recording()
        with self.lock:
            if self.colorwriter is not None:
                self.colorwriter.release()
            if self.depthwriter is not None:
                self.depthwriter.release()

    def record(self, data):
        super().record(data)
        if self.recording:
            # write the images
            if self.colorwriter is not None:
                self.colorwriter.write(self.color_image)
            if self.depthwriter is not None:
                self.depthwriter.write(self.depth_colormap)

    def shutdown(self):
        super().shutdown()
        if not self.simulate:
            self.pipeline.stop()
            print("camera closed cleanly")


def main(args=None):
    parameters = CameraHandler.get_parameters()
    camera_handler = CameraHandler(parameters)
    camera_handler.run()
    
if __name__ == '__main__':
    main()