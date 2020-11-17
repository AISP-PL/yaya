'''
Created on 17 lis 2020

@author: spasz
'''

import helpers.boxes as boxes

classNames=[]

def Init(names):
    ''' Initalize class names list'''
    global classNames
    classNames = names
     
def GetClassName(number):
    ''' Returns class name'''
    if (number < len(classNames)):
        return classNames[number]
    else:
        return 'Invalid'

def GetClassNumber(name):
    ''' Retruns class number '''
    return classNames.index(name)

def fromTxtAnnote(txtAnnote):
    ''' Creates Annote from txt annote.'''
    classNumber = int(txtAnnote[0])
    box = [ float(txtAnnote[1]), float(txtAnnote[2]), float(txtAnnote[3]), float(txtAnnote[4]) ]
    return Annote(box, classNumber==classNumber)

def fromDetection(detection):
    ''' Creates Annote from txt annote.'''
    className, confidence, box = detection
    return Annote(box, className=className, confidence=confidence)

class Annote():
    '''
    classdocs
    '''

    def __init__(self, box, classNumber=None, className=None, confidence=1.00):
        '''
        Constructor
        '''
        self.box = box
        self.confidence = confidence
        assert( (className!=None) or (classNumber!=None) )
        if (classNumber==None):
            self.className = className
            self.classNumber = GetClassNumber(self.className)        
        elif (className==None):
            self.classNumber = classNumber
            self.className = GetClassName(self.classNumber)        
        else:
            self.classNumber = classNumber
            self.className = className
            
    def Draw(self):
        ''' Draw self.'''
        
    def IsInside(self,point):
        ''' True if point is inside note box.'''
        return boxes.IsInside(point, self.box)

