# Blink Rate Detector
## Description
This project is a simple blink rate detector using a Raspberry Pi and a webcam. It uses the OpenCV library to detect faces and eyes, and then uses the number of blinks per minute to determine the blink rate. The blink rate is then displayed on a 16x2 LCD screen. The project is written in Python 3.7.3 and uses the OpenCV 4.1.0 library.

## Installation
### Hardware
* Raspberry Pi 3 Model B+
* Raspberry Pi Camera Module V2


### Software
* Python 3.7.3


## Usage
To run the program, run the following command in the terminal:
```
python3 blink_rate_detector.py
```

## Credits
* [Adrian Rosebrock](https://www.pyimagesearch.com/author/adrian/) for the [eye aspect ratio](https://www.pyimagesearch.com/2017/04/24/eye-blink-detection-opencv-python-dlib/) code
* 