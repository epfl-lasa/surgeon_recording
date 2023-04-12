# Surgeon recording

TODO : UPDATE README HERE 

This repository contains a library to record and read the flux of a several sensors such as Realsense camera, EMG, TPS
and Opitrack.

## Installation

For the installation of the software, follow [this](installation.md) guide.

## Recording data with the `recorder_app.py`

To record data, follow the [usage](usage.md) instructions.

## Reading data with the `reader_app.py`

After a recording session, all the data files should be located in `data` folder. You can create as many subdirectories
as you like to organise them. Launch the reader applet with:

```
cd path\to\recordings\surgeon_recording\
conda activate surgeon_recording
python reader_app.py
```

This serves a webpage locally that you can access using the navigator of your choice at the address `127.0.0.1:8050`.
Once loaded use it to analyze the data.

## Authors / Maintainers

- Baptiste Busch ([baptiste.busch@epfl.ch](mailto:baptiste.busch@epfl.ch))
- Dominic Reber ([dominic.reber@epfl.ch](mailto:dominic.reber@epfl.ch))