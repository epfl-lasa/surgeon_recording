import sys
import pathlib
import rclpy
import time
import numpy as np
import pandas as pd
import os
import cv2
import pyrealsense2 as rs
from rclpy.node import Node
from tf2_ros.transform_listener import TransformListener
from geometry_msgs.msg import TransformStamped
from tf2_ros.buffer import Buffer
from rclpy.duration import Duration
from tf2_ros import LookupException



# deifne the directory of the emgAcquireClient python_module 
emgAcquire_dir = "/home/ros2/ros2_ws/src/emgAcquire/python_module"

# append the path including the directory of the python_module
sys.path.append(emgAcquire_dir)

# import the module
import emgAcquireClient


class Recorder(Node):
    def __init__(self, data_folder):
        super().__init__('emg_recorder')
        self.data_folder = data_folder
        self.recording = False

        ######## User input ######
        self.task_folder = input("Enter task name : ")
        input("Press enter to start recording...")
        self.exp_folder = self.data_folder + "/" + self.task_folder + "/"
        if not os.path.exists(self.exp_folder):
            os.makedirs(self.exp_folder)

        ###### Optitrack #######
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)
        self.recorded_frames = ['blade', 'scissors', 'left_wrist', 'right_wrist', 'right_sup']
        self.opt_data = []
        self.create_timer(0.001, self.record_optitrack)

        ###### RealSense ######
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        color_path = self.exp_folder + 'rgb.avi'
        depth_path = self.exp_folder + 'depth.avi'
        self.colorwriter = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
        self.depthwriter = cv2.VideoWriter(depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)

        self.pipeline.start(self.config)
        self.create_timer(0.001, self.display_camera)

        ####### EMG ######
        # define number of channels to acquire
        self.nb_ch = 14
        emg_ip = "128.178.145.167"
        # create an emgClient object for acquiring the data
        self.emgClient = emgAcquireClient.emgAcquireClient(svrIP=emg_ip, nb_channels=self.nb_ch)
        # initialize the node
        init_test = self.emgClient.initialize()
        # start filling the buffer
        self.emgClient.start()
        self.emg_data = []
        self.create_timer(0.0001, self.record_emg)

        # start recording
        self.record()

    def display_camera(self):
        if self.recording:
            # Wait for a coherent pair of frames: depth and color
            frames = self.pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                return

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            # write the image
            self.colorwriter.write(color_image)
            self.depthwriter.write(depth_colormap)

            # Stack both images horizontally
            # images = np.hstack((color_image, depth_colormap))

            # # Show images
            # cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
            # cv2.imshow('RealSense', images)
            # cv2.waitKey(1)

    def record_emg(self):
        if self.recording:
            # append the array with the new data
            if len(self.emg_data) > 1:
                prev_time = self.emg_data[-1][0]
            else:
                prev_time = self.start_time
            # acquire the signals from the buffer
            emg_array = self.emgClient.getSignals()
            last_sample_time = time.time()
            dt = (last_sample_time - prev_time)/len(emg_array[0])
            for i in range(len(emg_array[0])):
                data = []
                t = prev_time + (i+1) * dt
                data.append(t)
                # keep the updating period
                data.append(t - self.start_time)
                data = data + emg_array[:, i].tolist()
                # append everything
                self.emg_data.append(data)

    def record_optitrack(self):
        if self.recording:
            absolute_time = time.time()
            data = [absolute_time, absolute_time - self.start_time]
            for f in self.recorded_frames:
                try:
                    tf = self._tf_buffer.lookup_transform(f, 'world', rclpy.time.Time(), timeout=Duration(seconds=0.01))
                    translation = tf.transform.translation
                    rotation = tf.transform.rotation
                    data = data + [translation.x, translation.y, translation.z, rotation.w, rotation.x, rotation.y, rotation.z]
                except LookupException:
                    self.get_logger().info("Frame " + f + " not visible")
                    return
            self.opt_data.append(data)

    def record(self):
        self.get_logger().info('Start recording')
        self.emg_data = []
        self.opt_data = []
        self.start_time = time.time()
        self.recording = True

    def stop(self):
        self.get_logger().info('Stop recording')
        self.recording = False

    def write_data(self):
        self.get_logger().info('Writing data')

        # optitrack data
        opt_header = ["absolute_time", "relative_time"]
        for f in self.recorded_frames:
            opt_header = opt_header + [f + "_x", f + "_y", f + "_z", f + "_qw", f + "_qx", f + "_qy", f + "_qz"]
        pd.DataFrame(self.opt_data).to_csv(self.exp_folder + "opt.csv", header=opt_header)

        # emg data
        emg_header = ["emg" + str(i) for i in range(self.nb_ch)]
        emg_header = ["absolute_time", "relative_time"] + emg_header
        pd.DataFrame(self.emg_data).to_csv(self.exp_folder + "emg.csv", header=emg_header)

    def shutdown(self):
        self.emgClient.shutdown()
        self.colorwriter.release()
        self.depthwriter.release()
        self.pipeline.stop()


def main(args=None):
    rclpy.init(args=args)

    # define the folder
    subject_folder = "fleur"

    # create variables
    data_folder = "/home/ros2/data/" + subject_folder
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    recorder = Recorder(data_folder)
    try:
        rclpy.spin(recorder)
    except KeyboardInterrupt:
        pass
    recorder.stop()
    recorder.shutdown()
    recorder.write_data()

    recorder.destroy_node()
    rclpy.shutdown()
    

    # shutdown the acquisition node
    
    
if __name__ == '__main__':
    main()