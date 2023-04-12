from surgeon_recording.sensor_handlers.camera_handler import CameraHandler
import zmq
import time

def main(args=None):
    parameters = CameraHandler.get_parameters()
    ip = parameters["streaming_ip"]
    port = parameters["port"]

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s:%s" % (ip, port))
    socket.setsockopt(zmq.SUBSCRIBE, b'rgb')
    socket.setsockopt(zmq.SUBSCRIBE, b'depth')

    context = zmq.Context()
    socket_recorder = context.socket(zmq.REQ)
    socket_recorder.connect("tcp://%s:%s" % (ip, port + 1))

    count = 0
    images = {}
    while True:
        try:
            data = CameraHandler.receive_data(socket)
            images.update(data)

            if 'rgb' in images.keys() and 'depth' in images.keys():
                CameraHandler.display_images(images['rgb'], images['depth'])

        except KeyboardInterrupt:
            print('Interruption, shutting down')
            break
    
if __name__ == '__main__':
    main()