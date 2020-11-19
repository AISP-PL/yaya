![title](doc/title.png)

# yolo-annotate

**Yet Another yolo annotation program**. Yolo_mark clone with openCV gui, but ...

- Rewritten in python,
- Checks for errors of overriding boxes,
- Auto-annotation feature added  - use yolo to detect and describe annotations of your image,
- Manual Yolo detection by presing 'd' - to check YOLO with original data,
- You can use standard YOLOv4 (MSCOCO) or your custom YOLOv4

### How to start?

`./yolo-annotate.py -i input/`


### Key codes

'''shell
LPM - create annotation
d - run detector
r - remove annotation
c - clear all annotations
s - save all (if errors not exists)
arrow -> or . - next image
arrow <- or , - previous image
'''


### Command line

'''shell
usage: yolo-annotate.py [-h] -i INPUT [-c CONFIG] [-on] [-yc] [-v]

optional arguments:
  -h, --help       show this help message and exit
  -i INPUT, --input INPUT
             Input path
  -c CONFIG, --config CONFIG
             Config path
  -on, --onlyNewFiles  Process only files without detections file.
  -yc, --yoloCustom   Use custom YOLO.
  -v, --verbose     Show verbose finded and processed data
'''

## Quick start

### 1. Darknet

Compile darknet and install libdarknet.so

### 2. Yolov4

Download YOLOv3 weights and copy to yolov4 directory.
