# Surgeon recording scripts

This script records the flux of a Realsense camera, EMG, TPS and Opitrack data.

## Installation

To install all the necessary packages, create a new environment with `conda` and install them using the `requirements.txt` file (replace `myenvname` with the name of your choice):

```
conda create --name myenvname python=3.7
conda activate myenvname
pip install -r requirements.txt
```

## Reading data with the `reader_app.py`

All the data files should be located in `data` folder. You can create as many subdirectories as you like to organise them. Launch the reader applet with:

```
python reader_app.py
```

This serves a webpage locally that you can access using the navigator of your choice at the address `127.0.0.1:8050`. Once loaded use it to analyze the data.