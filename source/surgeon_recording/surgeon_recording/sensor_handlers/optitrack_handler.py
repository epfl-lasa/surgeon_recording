import numpy as np
import zmq
import time
import sys
from surgeon_recording.sensor_handlers.NatNetClient import NatNetClient
from surgeon_recording.sensor_handlers.sensor_handler import SensorHandler


class OptitrackHandler(SensorHandler):
    def __init__(self, parameters):
        SensorHandler.__init__(self, 'optitrack', parameters)
        
        if self.running:
            self.timeout = parameters['frame_timeout']
            self.data_received = False
            self.received_frames = {}
            for frame in parameters['frames']:
                label = frame['label']
                self.received_frames[frame['streaming_id']] = {'label': label, 'position': [], 'orientation': [], 'timestamp': 0}

            if not self.simulated:
                self.opt_client = NatNetClient()
                # Configure the streaming client to call our rigid body handler on the emulator to send data out.
                self.opt_client.newFrameListener = self.receive_frame
                self.opt_client.rigidBodyListener = self.receive_rigid_body
                # Start up the streaming client now that the callbacks are set up.
                # This will run perpetually, and operate on a separate thread.
                self.opt_client.run()

    @staticmethod
    def get_parameters():
        parameters = SensorHandler.read_config_file('optitrack')
        if parameters['status'] != 'off' and parameters['status'] != 'remote':
            header = []
            for frame in parameters['frames']:
                label = frame['label']
                header = header + [label + '_x', label + '_y', label + '_z', label + '_qx', label + '_qy', label + '_qz', label + '_qw']
            parameters.update({ 'header': header })
        return parameters

    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body(self, id, position, rotation):
        with self.lock:
            if id in self.received_frames.keys():
                self.received_frames[id]['timestamp'] = time.time()
                self.received_frames[id]['position'] = position
                self.received_frames[id]['orientation'] = rotation
                self.data_received = True

    # This is a callback function that gets connected to the NatNet client and called once per mocap frame.
    def receive_frame(self, frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                      labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
        return

    def acquire_data(self):
        data = []
        if self.data_received:
            absolute_time = time.time()
            data = [self.index + 1, absolute_time, absolute_time - self.start_time]
            for key, f in self.received_frames.items():
                if absolute_time - f['timestamp'] < self.timeout:
                    for pos in f['position']:
                        data.append(pos)
                    for rot in f['orientation']:
                        data.append(rot)
                else:
                    print('Frame ' + f['label'] + ' not visible')
                    return []
            self.index = data[0]
        elif self.simulated:
            absolute_time = time.time()
            data = [self.index + 1, absolute_time, absolute_time - self.start_time]
            tmp = self.generate_fake_data(len(self.received_frames.keys()) * 7)
            for v in tmp:
                data.append(v)
            self.index = data[0]
        return data 

    def shutdown(self):
        super().shutdown()
        if not self.simulated:
            self.opt_client.shutdown()
        print('optitrack closed cleanly')


def main(args=None):
    parameters = OptitrackHandler.get_parameters()
    opt_handler = OptitrackHandler(parameters)
    opt_handler.run()
    
if __name__ == '__main__':
    main()
