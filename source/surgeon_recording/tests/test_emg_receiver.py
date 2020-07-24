from surgeon_recording.emg_handler import EMGHandler
import zmq
import time

def main(args=None):
    parameters = EMGHandler.get_parameters()
    ip = parameters["streaming_ip"]
    port = parameters["port"]

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s:%s" % (ip, port))
    socket.setsockopt(zmq.SUBSCRIBE, b'emg')

    context = zmq.Context()
    socket_recorder = context.socket(zmq.REQ)
    socket_recorder.connect("tcp://%s:%s" % (ip, port + 1))

    count = 0
    while True:
        try:
            signal = EMGHandler.receive_data(socket)
            print (signal)

        except KeyboardInterrupt:
            print('Interruption, shutting down')
            break
    
if __name__ == '__main__':
    main()