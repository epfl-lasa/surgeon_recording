# Surgeon recording scripts

This script records the flux of a Realsense camera, EMG and Opitrack data.

## Installing the realsense

You can follow the instructions on the GitHub: https://github.com/IntelRealSense/librealsense

Once installed on your computer you should be able to use `realsense-viewer` to see the camera.

## Installing Docker

The scripts require Docker to be started. Follow the instructions here https://docs.docker.com/engine/install/ubuntu/ and the postinstall instructions here https://docs.docker.com/engine/install/linux-postinstall/

## Recording

First you will need to build the Docker image with `sh build.sh`. Then you can run it with `sh run.sh`. This will open an interactive constainer in which you can use `ros2 run surgeon_recording recorder` to start the recording process.

If you want to record Optitrack data you will need a node in ROS1 that streams them. Then, you need to start the bridge between ROS1 and ROS2 with `sh run_bridge.sh`.

## Troubleshooting

If the script is showing nothing after pressing enter when prompted it is most likely that it can't open the camera. Verify that it works properly with `realsense-viewer` inside the Docker container. If not, `exit` the container and run `realsense-viewer` on the host. Then enter again the container with `sh run.sh`.