# Installation Instructions (Windows)

The following installation steps should work for a computer with an out-of-the-box Windows OS.

## Required Software

Start by downloading and installing the following applications (with default options, they will be configured in the
subsequent steps):

- [Anaconda](https://docs.anaconda.com/anaconda/install/windows/)
- [GitHub Desktop](https://desktop.github.com/)
- [Intel RealSense Viewer](https://www.intelrealsense.com/sdk-2/) (scroll down to find the download for the viewer)
- [Visual Studio](https://visualstudio.microsoft.com/downloads/) with the option *Desktop Development with C++* (and
  make sure *ATL* is part of it)
- [Motive](https://optitrack.com/support/downloads/motive.html) (including the `.NET` framework)
- [Visual Studio Code](https://code.visualstudio.com/download) (optionally, suggested editor)

## Acquisition Software Setup Steps

### EMG

1. Get the credit card shaped USB stick from the EMG box and install *Noraxon MR3.10* from the stick.

2. Download zip files ??? and put

3.

4. Turn on the Noraxon Desktop Receiver and plug it to the computer. Go to

### `surgeon_recording` Library

5. Open GitHub Desktop (you can skip the login steps if you want) and choose the option *Clone a repository from URL*,
   put [https://github.com/epfl-lasa/surgeon_recording.git](https://github.com/epfl-lasa/surgeon_recording.git) and
   choose a desired path (for example `C:\Users\USER\Documents\Recordings`), that will here be referred to
   as `path\to\recordings\`. Therefore, the GitHub repository will have the path `path\to\recordings\surgeon_recording`.

6. Launch Anaconda and open a Powershell Prompt from the available options. Then.
   ```bash
   cd path\to\recordings\surgeon_recording
   conda create -name surgeon_recording
   # confirm with yes
   conda activate surgeon_recording
   pip install -r .\requirements.txt
   cd .\source\surgeon_recording
   python .\setup.py develop
   ```
   This will install the library in the conda environment.

7. With an editor of your choice (Visual Studio Code is a good option), open
   the [emgAcquireClient.py](source/emgAcquireClient.py) file and edit the absolute path on line 7 such that
   `C:\Users\USER\path\to\recordings\surgeon_recording\source\emgAcquire\lib\win32\x64\emgAcquireClient.dll` is correct.

8. Then, open the [emg_handler.py](source/surgeon_recording/surgeon_recording/sensor_handlers/emg_handler.py) file and
   edit the absolute path on line 9 such
   that `r"C:\Users\USER\path\to\recordings\surgeon_recording\source\emgAcquire\python_module` is correct.

9. Then, open the [emgAcquireClient.py](source/emgAcquire/python_module/emgAcquireClient.py) file and edit the absolute
   path on line 10 such
   that `lib = ctypes.cdll.LoadLibrary(r'C:\Users\USER\path\to\recordings\surgeon_recording\source\emgAcquire\lib\win32\x64\emgAcquireClient.dll`
   is correct.

### First Test

After completing steps 1 to 9 it would be best to the test the setup that you have so far. For that, edit
the [sensor parameters file](source/surgeon_recording/config/sensor_parameters.json) such that the status of all sensors
is set to `simulated` (except the ft_sensor which should stay `off`).

Then, in a first terminal (always choose Powershell Prompts from Anaconda):

```bash
cd path\to\recordings\surgeon_recording
conda activate surgeon_recording
python .\start_all_sensors.py
```

Everything should run without errors, otherwise you have to debug, check that the absolute paths are set correctly and
so on.

In a second terminal:

```bash
cd path\to\recordings\surgeon_recording
conda activate surgeon_recording
python .\recorder_app.py
```

Open a new browser tab and type `127.0.0.1:8080` in the URL field to access the web interface of the recorder app. Start
a recording with the name `test_simulated`, stop it after a short time and check that the
directory `path\to\recordings\surgeon_recording\data` contains a folder `test_simulated` that contains the non-empty
files *camera.csv, depth.avi, emg.csv, optitrack.csv, rgb.avi, tps.csv*.

### RealSense Camera

10. Connect the camera to the computer. Make sure to use a fast USB cable and port because the camera data is
    particularly heavy.

11. Open the Intel RealSense Viewer and check if any firmware update are required and install them. Then, change to `2D`
    view and turn on the stereo module to check that you are getting the RGB data. Close the viewer afterwards.

12. Open the *Camera* app of Windows and check that you get the RGB image of the camera.

### Motive

13. Power up the portable OptiTrack camera system, connect it to the computer and launch Motive. Be aware that without
    the OptiTrack plugged in, it is not possible to use Motive due to the lack of a license.

14. Find the *Streaming Pane* in the toolbar (the icon looks like a signal / antenna) and activate the first option
    called *Broadcast Frame Data*.

15. Define the desired rigid bodies by selecting markers and creating a rigid body from them. Then, go to the *Assets
    Pane* and edit the rigid bodies. Give them a name, a streaming ID, and put something around 30 for the smoothing
    value.

16. In the [sensor parameters file](source/surgeon_recording/config/sensor_parameters.json), put the rigid bodies into
    the list `frames` under `optitrack` with the corresponding labels and streaming IDs.

### Second Test

After step 16, let's do another test. Follow the instructions from [the first test](#first-test) (with a different
folder name, e.g. `test_cameras`), except that in the sensor parameters file you put `on` in the status of the camera
and optitrack. In the data folder, the *optitrack.csv, rgb.avi, depth,avi* files should now contain real data.

*IMPORTANT*: Motive has to be running in the background for this to work.

### TPS

17. unzip chameleon and install

18. plug receiver and tes

19. Unzip sahr and local windows debugger, fail

20. Open GitHub Desktop and clone the repository from the URL `https://github.com/Microsoft/vcpkg.git` and change the
    path to `path\to\recordings\vcpkg`.

21. In a Powershell Prompt, do

      ```bash
      cd path\to\recordings\vcpkg
      .\bootstrap-vcpkg.bat
      .\vcpkg.exe integrate install
      .\vcpkg.exe intstall cppzmq:x64-windows
      ```

22. Go back to Visual Studio and run the *Local Windows Debugger* again. This time, the build should be successful and
    open a terminal that is displaying several lines of information. At the end, it should say *FingerTPS CONNECTED
    SUCCESSFULLY*. If this is not the case, close the terminal, make sure step 7 is okay and then try again.

## Final Test

The installation of the software should now be complete. Head over to the [usage instructions](usage.md) to test your
installation with the complete setup and all sensors.