# Checklist and Instructions for Surgeon Recordings

## Checklist

The following sensors and items are required:

- RealSense RGB Camera, USB Cable

- OptiTrack Trio Camera with Tripod and Ground

- Fingertip Pressure Sensors TPS, Transmitter, USB Receiver, and Calibration Base

- EMG Sensors, Probes and Receiver

- USB Hub with at least 3 Ports (RealSense, OptiTrack, EMG, plus one extra...)

- Optitrack Markers including placeholders, armbands, etc.

- Glue, cable reel, tools, etc...

## Setup

#### RealSense

Plug the RealSense to the computer (preferrably directly to the computer instead of going through the hub), start the
Windows Camera app and check the image is correctly displayed. For the stereo or the motion module, check with *Intel
RealSense Viewer*. Close the apps after checking.

#### OptiTrack

Connect the OptiTrack Trio to the USB Hub. Then, start *Motive*, set the ground plane in the *Calibration System Tools*
panel under `Calibration` &rarr; `Set Ground Plane` on the right of the main window and test the OptiTrack setup with
the desired markers. Existing markers are listed in the *Asset Pane* window accessible in the tool bar. New marker
frames can be created by selecting the markers in the main window, rigth click and then `Rigid Body`
&rarr; `Create From Selected Markers`. The marker label and ID can also be seen and changed in the *Asset Pane* window.
Make sure to test the setup will all the desired markers and check if the OptiTrack system can distinguish and localize
them well. **Let *Motive* run in the background.**

#### TPS Calibration

Once the TPS Transmitter is turned on and the USB Receiver is plugged into the computer directly, run *Chameleon TVR* as
administrator and let it connect to the sensors. Select the profile (1 or 2) depending on the transmitter that is used (
they should be labeled). Additionaly, connect the Calibration Base to the USB Hub. Then, in the tool bar, go
on `Calibration` &rarr; `Calibrate FingerTPS System`. Specify in the GUI where the sensors are placed and begin the
calibration process by clicking on `begin` and by following the instructions. To ensure that the calibration was
successful, go to `C:` &rarr; `Program Files` &rarr; `Pressure Profile Systems` &rarr; `Chameleon TVR` &rarr; `setup`
and check if the modified date of the `-cal` file corresponds to the current time. Close *Chameleon* afterwards.

#### EMG

Disconnect the EMG Probes from power supply such that they start blinking, turn on the EMG Receiver and connect it to
the USB Hub.

## Recording

1. Start the *Anaconda Navigator*. Multiple PowerShell Prompts will have to be launched from there.

2. In the first terminal (T1), run
   ```
   cd .\path\to\recordings\surgeon_recording\
   python .\copy_tps_calibration.py
   ```
   to copy the calibration file to the correct directory. If this is unsuccessful, the calibration didn't work.

3. Still in T1, run
   ```
   cd .\source\emgAcquire\
   .\bin\emgAcquire.exe config.json
   ```
   to start the EMG. This will open a GUI. Click `OK`, wait for connection and check in T1 if data is transmitted. **Do
   not close T1**.

4. Start your editor, navigate to `path\to\recordings\surgeon_recording\source\config\` and open `sensor_parameters.jon`
   . Go through the file and adapt the parameters for your tracking setup. In particular, update the list of OptiTrack
   frames and TPS fingers with a label and the corresponding streaming ID. The streaming ID of the OptiTrack frames can
   be found in *Motive*, the one for the fingers is assigned during the calibration of the TPS sensors in the UI. Make
   sure the desired sensors have their status set to `on`.

5. Open the *watchmakingdatalog.sln* project in Visual Studio. In the tool bar, click on `Local Windows Debugger`.
   **This will open a prompt, do not close it until you finished recording.**


6. Open a second terminal (T2), run
   ```
   cd path\to\recordings\surgeon_recording\
   conda activate surgeon_recording
   python start_all_sensors.py
   ```

Check the output in T2 to see if the recording is successfully started.

7. Open a third terminal (T3), run
   ```
   cd path\to\recordings\surgeon_recording\
   conda activate surgeon_recording
   python recorder_app.py
   ```
   You can now access the web app and start recording data from there. Just type `http://127.0.0.1:8080` in your browser
   and use the web app to save the data.

9. To change from one surgeon to another, stop the process in T2, close the TPS prompt, recalibrate and copy the
   calibration file and execute step 5 and 6 again.
   