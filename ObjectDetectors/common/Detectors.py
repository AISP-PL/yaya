'''
Created on 23 lis 2020

@author: spasz
'''
import logging

# Wrappers for constructors and module imports.
# Info! Unfortunately there was no option to
# handle it without wrappers.
# ----------- Wrappers


def CreateDetectorYOLOv4GDDKiA(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorYOLOv4GDDKiA import DetectorYOLOv4GDDKiA
    return DetectorYOLOv4GDDKiA(gpuID)


def CreateDetectorYOLOv4COCO(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorYOLOv4COCO import DetectorYOLOv4COCO
    return DetectorYOLOv4COCO(gpuID)


def CreateDetectorYOLOv4CSPGDDKiA(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorYOLOv4CSPGDDKiA import DetectorYOLOv4CSPGDDKiA
    return DetectorYOLOv4CSPGDDKiA(gpuID)


def CreateDetectorYOLOv4CSPCOCO(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorYOLOv4CSPCOCO import DetectorYOLOv4CSPCOCO
    return DetectorYOLOv4CSPCOCO(gpuID)


def CreateDetectorYOLOv4ExtGDDKiA(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorYOLOv4ExtGDDKiA import DetectorYOLOv4ExtGDDKiA
    return DetectorYOLOv4ExtGDDKiA(gpuID)


def CreateDetectorYOLOv4ExtGDDKiALite(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorYOLOv4ExtGDDKiALite import DetectorYOLOv4ExtGDDKiALite
    return DetectorYOLOv4ExtGDDKiALite(gpuID)


def CreateDetectorYOLOv4Plates(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorYOLOv4Plates import DetectorYOLOv4Plates
    return DetectorYOLOv4Plates(gpuID)


def CreateDetectorDarkPlate(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorDarkPlate import DetectorDarkPlate
    return DetectorDarkPlate(gpuID)


def CreateDetectorYOLOv4ALPR(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorYOLOv4ALPR import DetectorYOLOv4ALPR
    return DetectorYOLOv4ALPR(gpuID)


def CreateDetectorOpenCV(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorOpenCV import DetectorOpenCV
    return DetectorOpenCV(gpuID)


def CreateDetectorEmpty(gpuID):
    ''' Detector constructor with module import '''
    from ObjectDetectors.DetectorEmpty import DetectorEmpty
    return DetectorEmpty(gpuID)


# List off all possible detectors to use
_detectors = {}
_detectors['DetectorYOLOv4GDDKiA'] = {
    'Name': 'DetectorYOLOv4GDDKiA',
    'Directory': 'ObjectDetectors/yolov4gddkia/',
                 'Constructor': CreateDetectorYOLOv4GDDKiA}
_detectors['DetectorYOLOv4COCO'] = {
    'Name': 'DetectorYOLOv4COCO',
    'Directory': 'ObjectDetectors/yolov4coco/',
                 'Constructor': CreateDetectorYOLOv4COCO}
_detectors['DetectorYOLOv4CSPGDDKiA'] = {
    'Name': 'DetectorYOLOv4CSPGDDKiA',
    'Directory': 'ObjectDetectors/yolov4cspgddkia/',
                 'Constructor': CreateDetectorYOLOv4CSPGDDKiA}
_detectors['DetectorYOLOv4CSPCOCO'] = {
    'Name': 'DetectorYOLOv4CSPCOCO',
    'Directory': 'ObjectDetectors/yolov4cspcoco/',
                 'Constructor': CreateDetectorYOLOv4CSPCOCO}
_detectors['DetectorYOLOv4ExtGDDKiA'] = {
    'Name': 'DetectorYOLOv4ExtGDDKiA',
    'Directory': 'ObjectDetectors/yolov4extgddkia/',
                 'Constructor': CreateDetectorYOLOv4ExtGDDKiA}
_detectors['DetectorYOLOv4ExtGDDKiALite'] = {
    'Name': 'DetectorYOLOv4ExtGDDKiALite',
    'Directory': 'ObjectDetectors/yolov4extgddkialite/',
                 'Constructor': CreateDetectorYOLOv4ExtGDDKiALite}
_detectors['DetectorYOLOv4Plates'] = {
    'Name': 'DetectorYOLOv4Plates',
    'Directory': 'ObjectDetectors/yolov4plates/',
                 'Constructor': CreateDetectorYOLOv4Plates}
_detectors['DetectorDarkPlate'] = {
    'Name': 'DetectorDarkPlate',
    'Directory': 'ObjectDetectors/darkplate/',
                 'Constructor': CreateDetectorDarkPlate}
_detectors['DetectorYOLOv4ALPR'] = {
    'Name': 'DetectorYOLOv4ALPR',
    'Directory': 'ObjectDetectors/yolov4alpr/',
                 'Constructor': CreateDetectorYOLOv4ALPR}
_detectors['DetectorOpenCV'] = {
    'Name': 'DetectorOpenCV',
    'Directory': '',
    'Constructor': CreateDetectorOpenCV}
_detectors['DetectorEmpty'] = {
    'Name': 'DetectorEmpty',
    'Directory': 'ObjectDetectors/yolov4extgddkia/',
    'Constructor': CreateDetectorEmpty}


def CreateDetector(name, gpuID=0):
    ''' Creates detector based on detector ID.'''
    if (name in _detectors.keys()):
        return _detectors[name]['Constructor'](gpuID)

    logging.error('(Detectors) Invalid detector!')
    return None


def GetDetectors():
    '''
        Return all detectors in
        dictionary form.
    '''
    return _detectors
