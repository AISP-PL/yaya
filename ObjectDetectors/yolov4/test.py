#!/usr/bin/python3
import darknet
import argparse
import sys
import cv2
import matplotlib.pyplot as plt

# Arguments and config
parser = argparse.ArgumentParser()
parser.add_argument('-ii', '--image', type=str,
                    required=False, help='image file')
parser.add_argument('-iv', '--video', type=str,
                    required=False, help='Video file')
parser.add_argument('-c', '--confidence', type=float, nargs='?', const=0.5, default=0.5,
                    required=False, help='YOLO object confidence')
parser.add_argument('-v', '--verbose', action='store_true',
                    required=False, help='Show verbose finded and processed data')
parser.add_argument('-s', '--save', action='store_true',
                    required=False, help='Save objects to directory')
args = parser.parse_args()

if (args.image is None and args.video is None):
    print('No input given!')
    sys.exit(-1)

configPath = './cfg/yolov4.cfg'
weightPath = './cfg/yolov4.weights'
metaPath = './cfg/coco.data'
net, classes, colors = darknet.load_network(configPath, metaPath, weightPath)


# Single image processing
if (args.image is not None):
    filename = args.image

    # Read image image
    im = cv2.imread(filename)
    imheight, imwidth, channels = im.shape

    # Create an image we reuse for each detect
    darknet_image = darknet.make_image(imwidth, imheight, channels)
    darknet.copy_image_from_bytes(darknet_image, im.tobytes())
    detections = darknet.detect_image(net, classes, darknet_image)
    print(detections)

    # Print output
    output_image = darknet.draw_boxes(detections, im, colors)
    plt.imshow(output_image)
    plt.show()
