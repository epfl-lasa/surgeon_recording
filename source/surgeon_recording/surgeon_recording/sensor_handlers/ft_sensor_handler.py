import zmq
import time
import numpy as np
import os
from os.path import join
from surgeon_recording.sensor_handlers.sensor_handler import SensorHandler


class FTSensorHandler(SensorHandler):
    def __init__(self, parameters):
        SensorHandler.__init__(self, 'ft_sensor', parameters)

        if self.running:
            ip = parameters["sensor_ip"]
            port = parameters["sensor_port"]

            if not self.simulated:
                # socket for receiving sensor data
                print("socket initializing")
                context = zmq.Context()
                self.data_socket = context.socket(zmq.SUB)
                self.data_socket.setsockopt(zmq.CONFLATE, 1)
                self.data_socket.connect("tcp://%s:%s" % (ip, port))
                self.data_socket.setsockopt( zmq.SUBSCRIBE, b"" )
                print("socket initialized")

    @staticmethod
    def get_parameters():
        parameters = SensorHandler.read_config_file('ft_sensor')
        if parameters['status'] != 'off':
            parameters.update({ 'header': ['force_x', 'force_y', 'force_z', 'torque_x', 'torque_y', 'torque_z'] })
        return parameters

    def acquire_data(self):
        absolute_time = time.time()
        data = [self.index + 1, absolute_time, absolute_time - self.start_time]
        if not self.simulated:
            tmp = np.array([float(x) for x in self.data_socket.recv_string().split(",")])
        else:
            tmp = self.generate_fake_data(6)
        
        data = data + tmp.tolist()
        self.index = data[0]
        return data

    def shutdown(self):
        super().shutdown()
        if not self.simulated:
            self.data_socket.close()
        print("ft_sensor closed cleanly")


def main(args=None):
    parameters = FTSensorHandler.get_parameters()
    ft_sensor_handler = FTSensorHandler(parameters)
    ft_sensor_handler.run()


if __name__ == '__main__':
    main()