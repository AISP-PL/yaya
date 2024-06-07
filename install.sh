#!/bin/bash

# Check .venv exists, if not exit with error
if [ ! -d ".venv" ]; then
    echo "Please create a virtual environment first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Hard bug fix for force opencv-python-headless
# @TODO: Resolve better in the future
pip uninstall opencv-pytho
pip install --upgrade opencv-python-headless==4.8.0.76

#install commands in /usr/bin/
sudo ln -sf $(pwd)/scripts/yolo-annotate.sh /usr/bin/yolo-annotate
sudo ln -sf $(pwd)/yolo-distribution.py /usr/bin/yolo-distribution
sudo ln -sf $(pwd)/yaya-list-annotations.py /usr/bin/yaya-list
sudo ln -sf $(pwd)/yaya-resize.py /usr/bin/yolo-reize
