'''
Created on 21 maj 2021

@author: spasz
'''
from engine.annote import GetClasses


class GuiClassKeycodes(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # Max possible class number
        self.maxClassNumber = 11
        # There is 12 useable keycodes and extra key code
        # as modifier. Keycodes are positioned identicall
        # like on a keyboard.
        self.keycodes = ['1', '2', '3', '4', '5', '6',
                         '7', '8', '9', '0', '-', '=',
                         '`'  # modifier
                         ]
        # Base offset, changed by modifier
        self.offset = 0
        # Base max offset, calculated based on max class number
        self.maxOffset = 0

        self.SetMaxClassNumber(len(GetClasses()))

    def SetMaxClassNumber(self, number):
        ''' Sets max possible class number.'''
        self.maxClassNumber = number
        # Calculate max offset
        self.maxOffset = int(self.maxClassNumber / 12)

    def IsClassKeycode(self, keycode) -> bool:
        ''' True if it's class keycode.'''
        if (keycode < 0x110000):
            return chr(keycode) in self.keycodes
        return False

    def GetClassNumber(self, keycode) -> int:
        ''' Returns class number from keycode.'''
        # Check all possibilities
        for i, code in enumerate(self.keycodes):
            # Offset modifier keycode
            if ('`' == chr(keycode)):
                # Increment offset
                self.offset += 1
                # Drop to first offset value if larger than max offset
                if (self.offset > self.maxOffset):
                    self.offset = 0
                # Return first class from begining
                return self.offset * 12
                break

            # One of 12 useable keycodes
            if (code == chr(keycode)):
                classNumber = self.offset*12 + i
                if (classNumber < self.maxClassNumber):
                    return classNumber
                else:
                    return self.maxClassNumber

        # Class 0 returned if not found
        return 0
