'''
Created on 18 lis 2020

@author: spasz
'''
import numpy as np
import logging
from . import boxes
from . import metrics


def FilterIOUbyConfidence(annotations, maxIOU=0.75):
    '''
        Filter annotation if has bigger IOU > maxIOU.
        Annotation with bigger confidence stays!
    '''
    # Create IOU results matrix
    n = len(annotations)
    results = np.zeros([n, n], dtype=np.float32)
    for i, annote1 in enumerate(annotations):
        for j, annote2 in enumerate(annotations):
            if(annote1 != annote2):
                results[i, j] = metrics.MetricIOU(
                    annote1.GetBox(), annote2.GetBox())

    # Parse each row of IOU matrix
    passed = []
    for i, annote in enumerate(annotations):
        isFiltered = False
        for j in range(n):
            # If IOU >= maxIOU
            if (results[i, j] >= maxIOU):
                # If confidence is smaller
                if (annote.GetConfidence() <= annotations[j].GetConfidence()):
                    isFiltered = True
                    break

        if (isFiltered == True):
            logging.info('Filtered out (%s, %2.2f).',
                         annote.GetClassName(), annote.GetConfidence())
        else:
            passed.append(annote)

    return passed
