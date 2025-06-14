# ChickenHouse

This project has 2 python files.
1. light_detection.py
2. chickenhouse_gui.py

The light detection.py file takes an image as an input and detects the time of the day based on the image brightness, red ratio and blue ratio whether it is morning or night. Then it passes these results to the other file chickenhouse_gui.py which has a frontend interface using Tinkter and the results get displayed.

## Steps to Run

1. Clone the repository using the following command one by one
   
    '
    git clone https://github.com/abdullahthegt/ChickenHouse
    '
   
    '
    cd ChickenHouse
    '

2. Run the python code
   
    First goto light_detection.py file and change the image that you want to run the detection on like the following
   
    '
    DEFAULT_IMAGE_PATH = "./images/day1.jpg" # OR "./images/night.jpeg"
    '
   
    and then run:
   
    '
    python chickenhouse_gui.py
    '
