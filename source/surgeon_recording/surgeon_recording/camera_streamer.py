import pyrealsense2 as rs
import numpy as np
import zmq
import cv2

class CameraStreamer(object):
    def __init__(self, ip="127.0.0.1", port="5556"):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.color_image = []
        self.depth_colormap = []

        try:
            self.pipeline.start(self.config)
        except:
            print("Error initializing the camera")

        try:
            context = zmq.Context()
            self.socket = context.socket(zmq.PUB)
            self.socket.bind("tcp://%s:%s" % (ip, port))
        except:
            print("Error initializing ZMQ sockets")

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

    def run(self):
        while True:
            try:
                self.acquire_images()
                self.send_images()
            except KeyboardInterrupt:
                print('Interruption, shutting down')
                break
        self.pipeline.stop()

def main(args=None):
    camera_stream = CameraStreamer()
    camera_stream.run()
    
if __name__ == '__main__':
    main()