import pyrealsense2 as rs
import numpy as np
import zmq
import cv2
import csv
from threading import Thread, Event
import os
from os.path import join
import time

class CameraHandler(object):
    def __init__(self, ip="127.0.0.1", port=5556):
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

        # socket for publisher
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://%s:%s" % (ip, port))
        self.socket.setsockopt(zmq.LINGER, 0)
        # socker for recorder server
        self.recorder_socket = context.socket(zmq.REP)
        self.recorder_socket.bind("tcp://%s:%s" % (ip, port + 1))
        self.recorder_socket.setsockopt(zmq.LINGER, 0)

        self.stop_event = Event()
        self.recording_thread = Thread(target=self.recording_request_handler)
        self.recording_thread.start()

    def acquire_images(self, display=True):
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

    def send_image(self, image_type, image):
        self.socket.send_string(image_type, zmq.SNDMORE)
        self.socket.send_pyobj(image)

    def send_images(self):
        self.send_image('rgb', self.color_image)
        self.send_image('depth', self.depth_colormap)

    @staticmethod
    def receive_image(socket):
        image_type = socket.recv_string()
        image = socket.recv_pyobj()
        return [image_type, image]

    @staticmethod
    def display_images(color_image, depth_image):
        # Stack both images horizontally
        images = np.hstack((color_image, depth_image))
        # # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        cv2.waitKey(1)

    def recording_request_handler(self):
        while not self.stop_event.wait(0.01):
            print('Waiting for commands')
            message = self.recorder_socket.recv_json()
            if message['recording'] and not self.recording:
                self.setup_recording(message['folder'], message['start_time'])
                self.recorder_socket.send_string("recording started")
                print('Recording started')
            elif not message['recording'] and self.recording:
                self.stop_recording()
                self.recorder_socket.send_string("recording stopped")
                print('Recording stopped')
            else:
                self.recorder_socket.send_string("recording" if self.recording else "not recording")

    def setup_recording(self, recording_folder, start_time):
        if not os.path.exists(recording_folder):
            os.makedirs(recording_folder)
        
        color_path = join(recording_folder, 'rgb.avi')
        depth_path = join(recording_folder, 'depth.avi')
        self.colorwriter = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
        self.depthwriter = cv2.VideoWriter(depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)

        f = open(join(recording_folder, "camera.csv"), 'w', newline='')
        self.writer = {"file": f, "writer": csv.writer(f)}
        self.writer["writer"].writerow(["index", "absolute_time", "relative_time"])

        self.camera_index = 0
        self.start_time = start_time
        self.recording = True

    def stop_recording(self):
        self.recording = False
        self.colorwriter.release()
        self.depthwriter.release()

    def record(self):
        if self.recording:
            absolute_time = time.time()
            data = [self.camera_index + 1, absolute_time, absolute_time - self.start_time]
            self.camera_index = data[0]   
            self.writer["writer"].writerow(data)
            # write the images
            self.colorwriter.write(self.color_image)
            self.depthwriter.write(self.depth_colormap)

    def shutdown(self):
        self.stop_event.set()
        self.pipeline.stop()
        self.socket.close()
        self.recorder_socket.close()
        self.recording_thread.join()

    def run(self):
        while True:
            try:
                self.acquire_images()
                self.record()
                self.send_images()
            except KeyboardInterrupt:
                print('Interruption, shutting down')
                break
        self.shutdown()

def main(args=None):
    camera_handler = CameraHandler()
    camera_handler.run()
    
if __name__ == '__main__':
    main()