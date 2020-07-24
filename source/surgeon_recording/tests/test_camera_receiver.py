from surgeon_recording.camera_handler import CameraHandler
import zmq
import time

def main(args=None):
    ip = "127.0.0.1"
    port = "5556"
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s:%s" % (ip, port))
    socket.setsockopt(zmq.SUBSCRIBE, b'rgb')
    socket.setsockopt(zmq.SUBSCRIBE, b'depth')

    port = "5557"
    context = zmq.Context()
    socket_recorder = context.socket(zmq.REQ)
    socket_recorder.connect("tcp://%s:%s" % (ip, port))

    count = 0
    images = {}
    while True:
        try:
            data = CameraHandler.receive_data(socket)
            images.update(data)

            if 'rgb' in images.keys() and 'depth' in images.keys():
                CameraHandler.display_images(images['rgb'], images['depth'])

            if count == 500:
                message = {'recording': True, 'folder': 'test', 'start_time': time.time()}
                socket_recorder.send_json(message)
                if socket_recorder.recv_string() == "recording started":
                    print('all good')

            if count == 2000:
                message = {'recording': False}
                socket_recorder.send_json(message)
                if socket_recorder.recv_string() == "recording stopped":
                    print('all good')
            count = count + 1

        except KeyboardInterrupt:
            print('Interruption, shutting down')
            break
    
if __name__ == '__main__':
    main()