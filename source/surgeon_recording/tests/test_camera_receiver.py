from surgeon_recording.camera_streamer import CameraStreamer
import zmq

def main(args=None):
    ip = "127.0.0.1"
    port = "5556"
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s:%s" % (ip, port))
    socket.setsockopt(zmq.SUBSCRIBE, b'rgb')
    socket.setsockopt(zmq.SUBSCRIBE, b'depth')

    images = {}
    while True:
        try:
            type_image, image = CameraStreamer.receive_image(socket)
            images[type_image] = image
            if 'rgb' in images.keys() and 'depth' in images.keys():
                CameraStreamer.display_images(images['rgb'], images['depth'])

        except KeyboardInterrupt:
            print('Interruption, shutting down')
            break
    
if __name__ == '__main__':
    main()