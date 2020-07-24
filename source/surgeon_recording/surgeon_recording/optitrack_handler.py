import numpy as np
import zmq
import time
import sys
from surgeon_recording.NatNetClient import NatNetClient
from surgeon_recording.sensor_handler import SensorHandler


class OptitrackHandler(SensorHandler):
    def __init__(self, parameters):
        SensorHandler.__init__(self, 'optitrack', parameters)
        self.timeout = parameters["frame_timeout"]
        self.received_frames = {}
        for frame in parameters["frames"]:
            label = frame["label"]
            self.received_frames[frame["streaming_id"]] = {"label": label, "position": [], "orientation": [], "timestamp": 0}
            
        
        self.opt_client = NatNetClient()
        # Configure the streaming client to call our rigid body handler on the emulator to send data out.
        self.opt_client.newFrameListener = self.receive_frame
        self.opt_client.rigidBodyListener = self.receive_rigid_body
        # Start up the streaming client now that the callbacks are set up.
        # This will run perpetually, and operate on a separate thread.
        # self.opt_client.run()

    @staticmethod
    def get_parameters():
        parameters = SensorHandler.read_config_file()
        param = parameters['optitrack']
        header = []
        for frame in param["frames"]:
            label = frame["label"]
            header = header + [label + "_x", label + "_y", label + "_z", label + "_qw", label + "_qx", label + "_qy", label + "_qz"]
        param.update({ 'header': header })
        return param

    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body(self, id, position, rotation):
        self.received_frames[id]["timestamp"] = time.time()
        self.received_frames[id]["position"] = position
        self.received_frames[id]["orientation"] = rotation

    # This is a callback function that gets connected to the NatNet client and called once per mocap frame.
    def receive_frame(self, frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                      labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
        return

    def acquire_data(self):
        absolute_time = time.time()
        data = [self.index + 1, absolute_time, absolute_time - self.start_time]
        for key, f in self.received_frames.items():
            if absolute_time - f["timestamp"] < self.timeout:
                for pos in f["position"]:
                    data.append(pos)
                for rot in f["orientation"]:
                    data.append(rot)
            else:
                print("Frame " + f["label"] + " not visible")
                #return
        self.index = data[0]
        
        tmp = self.generate_fake_data([1, 14])
        for v in tmp[0]:
            data.append(v)
        return data 

    def shutdown(self):
        super().shutdown()
        # self.opt_client.shutdown()


def main(args=None):
    parameters = OptitrackHandler.get_parameters()
    opt_handler = OptitrackHandler(parameters)
    opt_handler.run()
    
if __name__ == '__main__':
    main()