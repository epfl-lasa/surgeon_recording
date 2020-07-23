from surgeon_recording.emg_streamer import EMGStreamer
import zmq

def main(args=None):
    ip = "127.0.0.1"
    port = "5557"
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s:%s" % (ip, port))
    socket.setsockopt(zmq.SUBSCRIBE, b'emg')

    while True:
        try:
            signal = EMGStreamer.receive_signal(socket)
            print(signal)

        except KeyboardInterrupt:
            print('Interruption, shutting down')
            break
    
if __name__ == '__main__':
    main()