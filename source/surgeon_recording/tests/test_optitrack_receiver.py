from surgeon_recording.optitrack_handler import OptitrackHandler
import zmq
import time

def main(args=None):
    parameters = OptitrackHandler.get_parameters()
    ip = parameters["streaming_ip"]
    port = parameters["port"]

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s:%s" % (ip, port))
    socket.setsockopt(zmq.SUBSCRIBE, b'optitrack')

    context = zmq.Context()
    socket_recorder = context.socket(zmq.REQ)
    socket_recorder.connect("tcp://%s:%s" % (ip, port + 1))

    count = 0
    while True:
        try:
            signal = OptitrackHandler.receive_data(socket)
            print (signal)

        except KeyboardInterrupt:
            print('Interruption, shutting down')
            break
    
if __name__ == '__main__':
    main()