import zmq
import sys

if __name__ == "__main__":
     if len(sys.argv) != 2:
          print("Usage: provide the port you want to listen data from")
          sys.exit(1)
     
     aContext = zmq.Context()                                          # .new Context
     aSUB     = aContext.socket( zmq.SUB )                             # .new Socket
     aSUB.connect( "tcp://127.0.0.1:" + sys.argv[1] )                            # .connect
     aSUB.setsockopt( zmq.LINGER, 0 )                                  # .set ALWAYS!
     aSUB.setsockopt( zmq.SUBSCRIBE, b"" )                              # .set T-filter

     MASK = "INF: .recv()-ed this:[{0:}]\n:     waited {1: > 7d} [us]"
     aClk = zmq.Stopwatch(); 

     while True:
          try:
               aClk.start(); print(MASK.format( aSUB.recv(),
                                             aClk.stop()
                                             ))
          except ( KeyboardInterrupt, SystemExit ):
               pass
               break
     pass
     aSUB.close()                                                     # .close ALWAYS!
     aContext.term()