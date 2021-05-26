'''
Created on 21 maj 2021

@author: spasz
'''


class GuiClassKeycodes(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.keycodes = ['0', '1', '2', '3', '4',
                         '5', '6', '7', '8', '9',
                         '-', '=']

    def IsClassKeycode(self, keycode) -> bool:
        ''' True if it's class keycode.'''
        if (keycode < 0x110000):
            return chr(keycode) in self.keycodes
        return False

    def GetClassNumber(self, keycode) -> int:
        ''' Returns class number from keycode.'''
        # Check all possibilities
        for i, code in enumerate(self.keycodes):
            if (code == chr(keycode)):
                return i

        # Class 0 returned if not found
        return 0
