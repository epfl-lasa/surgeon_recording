import zmq
import time
import numpy as np
import os
from os.path import join
from surgeon_recording.sensor_handlers.sensor_handler import SensorHandler


class FTSensorHandler(SensorHandler):
    def __init__(self, parameters):
        SensorHandler.__init__(self, 'ft_sensor', parameters)
        ip = parameters["sensor_ip"]
        port = parameters["sensor_port"]
        self.simulate = parameters["simulate"]

        if not self.simulate:
            # socket for receiving sensor data
            print("socket initializing")
            context = zmq.Context()
            self.data_socket = context.socket(zmq.SUB)
            self.data_socket.connect("tcp://%s:%s" % (ip, port))
            self.data_socket.subscribe(b'ft_sensor_data')
            self.data_socket.setsockopt(zmq.SNDHWM, 5)
            self.data_socket.setsockopt(zmq.SNDBUF, 5*1024)
            print("socket initialized")

    @staticmethod
    def get_parameters():
        parameters = SensorHandler.read_config_file()
        param = parameters['ft_sensor']
        param.update({ 'header': ['force_x', 'force_y', 'force_z', 'torque_x', 'torque_y', 'torque_z'] })
        return param

    def acquire_data(self):
        absolute_time = time.time()
        data = [self.index + 1, absolute_time, absolute_time - self.start_time]
        if not self.simulate:
            topic = self.data_socket.recv_string()
            tmp = np.array([float(x) for x in self.data_socket.recv_string().split(",")])
        else:
            tmp = self.generate_fake_data(6)
        
        data = data + tmp.tolist()
        self.index = data[0]
        return data

    def shutdown(self):
        super().shutdown()
        self.data_socket.close()
        print("ft_sensor closed cleanly")


def main(args=None):
    parameters = FTSensorHandler.get_parameters()
    ft_sensor_handler = FTSensorHandler(parameters)
    ft_sensor_handler.run()


if __name__ == '__main__':
    main()