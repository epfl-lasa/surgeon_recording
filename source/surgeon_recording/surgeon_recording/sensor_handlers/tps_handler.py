import zmq
import time
from surgeon_recording.sensor_handlers.sensor_handler import SensorHandler

class TPSHandler(SensorHandler):
    def __init__(self, parameters):
        SensorHandler.__init__(self, 'tps', parameters)
        ip = parameters["sensor_ip"]
        port = parameters["sensor_port"]

        # socket for receiving sensor data

        print("socket initializing")
        context = zmq.Context()
        self.data_socket = context.socket(zmq.SUB)
        self.data_socket.connect("tcp://%s:%s" % (ip, port))
        self.data_socket.setsockopt(zmq.SUBSCRIBE, b'tps_data')
        print("socket initialized")

    @staticmethod
    def get_parameters():
        parameters = SensorHandler.read_config_file()
        param = parameters['tps']
        param.update({ 'header': [] })
        return param

    def acquire_data(self):
        topic = self.data_socket.recv_string()
        data = map(float, self.data_socket.recv_string().split(","))
        return data

    def shutdown(self):
        super().shutdown()
        self.data_socket.close()


def main(args=None):
    parameters = TPSHandler.get_parameters()
    tps_handler = TPSHandler(parameters)
    tps_handler.run()
    
if __name__ == '__main__':
    main()