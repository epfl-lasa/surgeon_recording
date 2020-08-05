import subprocess
from os.path import join
import time

if __name__ == '__main__':
    script_folder = join('source', 'surgeon_recording', 'surgeon_recording', 'sensor_handlers')
    sensors = ['camera', 'emg', 'tps', 'optitrack']
    processes = []
    for s in sensors:
        processes.append(subprocess.Popen(['python', join(script_folder, s + '_handler.py')]))

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
                print('Interruption, shutting down')
                break
    for p in processes:
        p.terminate()