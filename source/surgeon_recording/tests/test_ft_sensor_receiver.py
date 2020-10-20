from surgeon_recording.sensor_handlers.ft_sensor_handler import FTSensorHandler
import zmq
import time

def main(args=None):
    parameters = FTSensorHandler.get_parameters()
    ip = parameters["streaming_ip"] if parameters["streaming_ip"] != "*" else "127.0.0.1"
    port = parameters["streaming_port"]

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s:%s" % (ip, port))
    socket.setsockopt(zmq.SUBSCRIBE, b'ft_sensor')
    socket.setsockopt(zmq.RCVHWM, 10)
    socket.setsockopt(zmq.RCVBUF, 10*1024)

    context = zmq.Context()
    socket_recorder = context.socket(zmq.REQ)
    socket_recorder.connect("tcp://%s:%s" % (ip, port + 1))

    count = 0
    while True:
        try:
            signal = FTSensorHandler.receive_data(socket)
            print (signal)

        except KeyboardInterrupt:
            print('Interruption, shutting down')
            break
    
if __name__ == '__main__':
    main()