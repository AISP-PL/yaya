'''
    Test benchmark of NMS methods.
'''
import time
import pytest
import random
import numpy as np
from ObjectDetectors.common.Detector import NmsMethod
from helpers.ensemble_boxes_nmw import non_maximum_weighted
from helpers.ensemble_boxes_wbf import weighted_boxes_fusion
from helpers.ensemble_boxes_nms import nms, soft_nms


def DetectionsCreate(count: int = 1000,
                     imwidth: int = 1920,
                     imheight: int = 1080,
                     detMaxWidth: int = 200,
                     detMinWidth: int = 40,
                     classes: int = 22):
    ''' Create three lists of boxes, scores, classids.'''

    # Boxes : Create list of random rects (x1,y1,x2,y2) inside image
    # Random center point and width. Always square.
    boxes = []
    for i in range(count):
        width = random.randint(detMinWidth, detMaxWidth)
        xc = random.randint(width, imwidth)
        yc = random.randint(width, imheight)
        x1 = xc - width/2
        y1 = yc - width/2
        x2 = xc + width/2
        y2 = yc + width/2
        # Append to boxes list, always int(), as tuple.
        boxes.append((int(x1), int(y1), int(x2), int(y2)))

    # Scores : Create list of random scores, with numpy random.
    scores = np.random.rand(count).tolist()

    # Classes IDs : Create list of random class ids from 0 to classes-1.
    classids = np.random.randint(0, classes, count).tolist()

    # Return detections
    return boxes, scores, classids


def EnsembleBoxes(boxes, scores, classids,
                  nmsMethod: NmsMethod = NmsMethod.Nms,
                  iou_thresh=0.45,
                  conf_thresh=0.5,
                  ) -> tuple:
    ''' Ensbmle boxes using given method.'''
    if (nmsMethod == NmsMethod.Nms):
        return nms([boxes], [scores], [classids], iou_thr=iou_thresh)
    elif (nmsMethod == NmsMethod.SoftNms):
        return soft_nms([boxes], [scores], [classids], iou_thr=iou_thresh, thresh=conf_thresh)
    elif (nmsMethod == NmsMethod.NmWeighted):
        npboxes, npscores, npclassids = non_maximum_weighted(
            [boxes], [scores], [classids], iou_thr=iou_thresh, skip_box_thr=conf_thresh)
        return npboxes.tolist(), npscores.tolist(), npclassids.tolist()

    elif (nmsMethod == NmsMethod.WeightedBoxFusion):
        return weighted_boxes_fusion([boxes], [scores], [classids], iou_thr=iou_thresh, skip_box_thr=conf_thresh)


def test_benchmark_nms(count: int = 1000):
    ''' Benchmark test of all nms methods'''

    # Detection create all
    boxes, scores, classids = DetectionsCreate(count=count)

    for method in NmsMethod:
        # Reset detections
        detections = boxes.copy(), scores.copy(), classids.copy()

        # Ensemble boxes
        startTime = time.time()
        EnsembleBoxes(*detections, nmsMethod=method)

        # Results
        endTime = time.time()
        duration = endTime - startTime
        fps = count / duration
        print(
            f'Method: {method}, Count: {count}, Duration: {duration:.3f} s, FPS: {fps:.1f}')

    print('Done.')


if __name__ == '__main__':
    test_benchmark_nms()
