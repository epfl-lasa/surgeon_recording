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

## Get Additional Installation Files

Additional installation and setup files are required to complete the installation steps below. The files can be
requested from [dominic.reber@epfl.ch](mailto:dominic.reber@epfl.ch) and come as zipped folders.

Unzip *SDK Package.zip*, *Noraxon.Acquire.zip*, and *Chameleon Installer-EPFL1 & 2.zip* somewhere on your computer and
make sure that the folder structure is as follows:

```bash
path\to\unzipped\folders
└──SDK Package
└──Noraxon.Acquire
└──Chameleon Installer-EPFL1 & 2
```

## Acquisition Software Setup Steps

### EMG

1. Get the credit card shaped USB stick from the EMG box and install *Noraxon MR3.10* from the stick.

2. With the explorer, go to `path\to\unzipped\folders\SDK Package` and run `Noraxon.Acquire.1.7.65.0.exe`. Continue with
   the installation even if Windows complains and leave the default values as is.

3. Turn on the Noraxon Desktop Receiver and plug it to the computer. With the explorer, go
   to `path\to\unzipped\folders\Noraxon.Acquire\src\easy2\acquirecom` and run `test.exe`. A window should open up that
   shows three devices, one of which should bee the Noraxon Desktop Receiver. Drag and drop this one to the left, and
   the other two to the right. A configuration window for the Desktop Receiver will pop up, choose *Detect
   Configuration* and accept. Confirm and close the windows.

### `surgeon_recording` Library

4. Open GitHub Desktop (you can skip the login steps if you want) and choose the option *Clone a repository from URL*,
   put [https://github.com/epfl-lasa/surgeon_recording.git](https://github.com/epfl-lasa/surgeon_recording.git) and
   choose a desired path (for example `C:\Users\USER\Documents\Recordings`), that will here be referred to
   as `path\to\recordings\`. Therefore, the GitHub repository will have the path `path\to\recordings\surgeon_recording`.

5. Launch Anaconda and open a PowerShell Prompt from the available options. Then.
   ```bash
   cd path\to\recordings\surgeon_recording
   conda create --name surgeon_recording python=3.8
   # confirm with yes
   conda activate surgeon_recording
   pip install -r .\requirements.txt
   cd .\source\surgeon_recording
   python .\setup.py develop
   ```
   This will install the library in the conda environment.

6. With an editor of your choice (Visual Studio Code is a good option), open
   the [emgAcquireClient.py](source/emgAcquireClient.py) file and edit the absolute path on line 7 such that
   `C:\Users\USER\path\to\recordings\surgeon_recording\source\emgAcquire\lib\win32\x64\emgAcquireClient.dll` is correct.

7. Then, open the [emg_handler.py](source/surgeon_recording/surgeon_recording/sensor_handlers/emg_handler.py) file and
   edit the absolute path on line 9 such
   that `r"C:\Users\USER\path\to\recordings\surgeon_recording\source\emgAcquire\python_module` is correct.

8. Then, open the [emgAcquireClient.py](source/emgAcquire/python_module/emgAcquireClient.py) file and edit the absolute
   path on line 10 such
   that `lib = ctypes.cdll.LoadLibrary(r'C:\Users\USER\path\to\recordings\surgeon_recording\source\emgAcquire\lib\win32\x64\emgAcquireClient.dll`
   is correct.

### First Test

After completing steps 1 to 8 it would be best to the test the setup that you have so far. For that, edit
the [sensor parameters file](source/surgeon_recording/config/sensor_parameters.json) such that the status of all sensors
is set to `simulated` (except the ft_sensor which should stay `off`).

Then, in a first terminal (always choose PowerShell Prompts from Anaconda):

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

9. Connect the camera to the computer. Make sure to use a fast USB3 cable and port because the camera data is
   particularly heavy.

10. Open the Intel RealSense Viewer and check if any firmware update are required and install them. Then, change to `2D`
    view and turn on the stereo module to check that you are getting the RGB data. Close the viewer afterwards.

11. Open the *Camera* app of Windows and check that you get the RGB image of the camera.

### Motive

12. Power up the portable OptiTrack camera system, connect it to the computer and launch Motive. Be aware that without
    the OptiTrack plugged in, it is not possible to use Motive due to the lack of a license.

13. Find the *Streaming Pane* in the toolbar (the icon looks like a signal / antenna) and activate the first option
    called *Broadcast Frame Data*.

14. Define the desired rigid bodies by selecting markers and creating a rigid body from them. Then, go to the *Assets
    Pane* and edit the rigid bodies. Give them a name, a streaming ID, and put something around 30 for the smoothing
    value.

15. In the [sensor parameters file](source/surgeon_recording/config/sensor_parameters.json), put the rigid bodies into
    the list `frames` under `optitrack` with the corresponding labels and streaming IDs.

### Second Test

After step 16, let's do another test. Follow the instructions from [the first test](#first-test) (with a different
folder name, e.g. `test_cameras`), except that in the sensor parameters file you put `on` in the status of the camera
and optitrack. In the data folder, the *optitrack.csv, rgb.avi, depth,avi* files should now contain real data.

**IMPORTANT**: Motive has to be running in the background for this to work.

### TPS

16. With the explorer, go to `path\to\unzipped\folders\Chameleon Installer-EPFL1 & 2` and
    run `Install_Chameleon_TVR.exe`. Continue with the installation even if Windows complains and leave the default
    values as is.

17. Plug in the red USB receiver with number 184A57, turn on the transmitter box with number two, and connect a finger.
    Run Chameleon as admin and choose configuration *EPFL-S2*, check that the connection is established successfully and
    that you see the sensor data when squeezing the finger. Close Chameleon afterwards.

18. To run Chameleon as admin per default, go to *Start* - *Chameleon TVR 2017* - *right click* and then instead of
    choosing *Run as administrator*, choose *Open file location*. Then right click on the executable file in the
    explorer, choose *Properties* and then in the window, go to *Shortcut* - *Advanced...* and check the box beside *Run
    as administrator*. Confirm, apply the changes and then close the window.

19. From the additional installation files, unzip *SAHR_data_recording* and put the folder to `path\to\recordings`.
    Then, open `path\to\recordings\SAHR_data_recording\WatchmakingDataLog.sln` with Visual Studio. Click on the *Local
    Windows Debugger* without changing anything. The build should fail.

20. Open GitHub Desktop and clone the repository from the URL `https://github.com/Microsoft/vcpkg.git` and change the
    path to `path\to\recordings\vcpkg`.

21. In a PowerShell Prompt, do

      ```bash
      cd path\to\recordings\vcpkg
      .\bootstrap-vcpkg.bat
      .\vcpkg.exe integrate install
      .\vcpkg.exe intstall cppzmq:x64-windows
      ```

22. Go back to Visual Studio and run the *Local Windows Debugger* again. This time, the build should be successful and
    open a terminal that is displaying several lines of information. At the end, it should say *FingerTPS CONNECTED
    SUCCESSFULLY*. If this is not the case, close the terminal, make sure step 17 is okay and then try again.

## Final Test

The installation of the software should now be complete. Head over to the [usage instructions](usage.md) to test your
installation with the complete setup and all sensors.
