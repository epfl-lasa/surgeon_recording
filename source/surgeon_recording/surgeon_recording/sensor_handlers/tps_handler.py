import zmq
import time
from surgeon_recording.sensor_handlers.sensor_handler import SensorHandler

class TPSHandler(SensorHandler):
    def __init__(self, parameters):
        SensorHandler.__init__(self, 'tps', parameters)
        ip = parameters["sensor_ip"]
        port = parameters["sensor_port"]
        self.simulate = parameters["simulate"]

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
        param.update({ 'header': ["tps" + str(i) for i in range(param["nb_adapters"] * 6)] })
        return param

    def acquire_data(self):
        absolute_time = time.time()
        data = [self.index + 1, absolute_time, absolute_time - self.start_time]
        if not self.simulate:
            topic = self.data_socket.recv_string()
            tmp = [float(x) for x in self.data_socket.recv_string().split(",")[:-1]]
        else:
            tmp = self.generate_fake_data(12)
        for v in tmp:
                data.append(v)
        self.index = data[0]
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