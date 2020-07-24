import numpy as np
import zmq

class EMGStreamer(object):
	def __init__(self, nb_channels, emg_ip="localhost", streaming_ip="127.0.0.1", port="5557"):
        # define number of channels to acquire
        self.nb_channels = nb_channels
        # create an emgClient object for acquiring the data
        self.emgClient = emgAcquireClient.emgAcquireClient(svrIP=emg_ip, nb_channels=self.nb_channels)
        # initialize the node
        init_value = self.emgClient.initialize()
        self.emg_init = init_value == 0
        self.emg_array = []

        try:
            context = zmq.Context()
            self.socket = context.socket(zmq.PUB)
            self.socket.bind("tcp://%s:%s" % (streaming_ip, port))
        except:
            print("Error initializing ZMQ sockets")

    def acquire_emg(self):
    	# acquire the signals from the buffer
        self.emg_array = self.emgClient.getSignals()

    def send_signal(self):
    	self.socket.send_string('emg', zmq.SNDMORE)
        self.socket.send_pyobj(self.emg_array)

    @staticmethod
    def receive_signal(socket):
    	socket.recv_string()
    	return socket.recv_pyobj()

   	def run(self):
   		self.emgClient.start()
        while True:
            try:
                self.acquire_emg()
                self.send_signal()
            except KeyboardInterrupt:
                print('Interruption, shutting down')
                break
        self.emgClient.shutdown()