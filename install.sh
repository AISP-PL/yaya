#!/bin/bash

#install commands in /usr/bin/
sudo ln -sf $(pwd)/scripts/yolo-annotate.sh /usr/bin/yolo-annotate
sudo ln -sf $(pwd)/yolo-distribution.py /usr/bin/yolo-distribution
sudo ln -sf $(pwd)/yaya-list-annotations.py /usr/bin/yaya-list
sudo ln -sf $(pwd)/yaya-resize.py /usr/bin/yolo-reize
