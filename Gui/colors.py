'''
Created on 23 lis 2020

@author: spasz
'''

from random import randint
import logging

# Colors standard in OpenCV is BGR
white = (255, 255, 255)
darkgray = (64, 64, 64)
gray = (128, 128, 128)
lightgray = (192, 192, 192)
black = (0, 0, 0)
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
pink = (0, 255, 255)
magenta = pink  # pink ~= magenta
cyan = (255, 255, 0)
yellow = (255, 0, 255)
orange = (0, 140, 255)
brown = (19, 69, 139)
indigo = (130, 0, 75)
teal = (128, 128, 0)
olive = (0, 128, 0)
maroon = (0, 0, 128)
cornflowerblue = (237, 149, 100)
darksalmon = (122, 150, 233)

# Color schemes
# ----------------

# Color table used for next table color method (BGR)
colorSchemeBright = [
    red,
    blue,
    yellow,
    green,
    pink,
    orange,
    indigo,
    cyan,
    brown,
    teal,
    olive,
    maroon,
    cornflowerblue,
]

# Default matplotlib color cycler (BGR)
colorSchemeMatplotlib = [
    (0xb4, 0x77, 0x1f),
    (0x0e, 0x7f, 0xff),
    (0x2c, 0xa0, 0x2c),
    (0x28, 0x27, 0xd6),
    (0xbd, 0x67, 0x94),
    (0x4b, 0x56, 0x8c),
    (0xc2, 0x77, 0xe3),
    (0x7f, 0x7f, 0x7f),
    (0x22, 0xbd, 0xbc),
    (0xcf, 0xbe, 0x17),
    (0x33, 0x33, 0x33),
    red,
    blue,
    green,
    magenta,
    cyan,
]


class ColorCycler:
    '''
    classdocs
    '''

    def __init__(self, scheme=None):
        ''' Constructor.'''
        if (scheme is None):
            logging.fatal('(ColorCycler) Invalid color scheme!')

        # Save color scheme
        self.scheme = scheme
        # Color cycler index
        self.index = 0

    def GetColor(self, index):
        ''' Get color stored with index.'''
        return self.scheme[index % len(self.scheme)]

    def GetNextColor(self):
        ''' Return next color.'''
        # Store color
        color = self.scheme[self.index]
        # Increment index
        self.index += 1
        if (self.index == len(self.scheme)):
            self.index = 0

        return color

    def Reset(self):
        ''' Reset color cycler index.'''
        self.index = 0


# Default color cycler
defaultColorCycler = ColorCycler(scheme=colorSchemeBright)


def toMatplotlibColor(rgb, alpha=1):
    ''' Convert single RGB color to matplotlib color.'''
    r, g, b = rgb
    return (r, g, b, alpha)


def GetOpposedColor(color):
    ''' Returns opposed color.'''
    r, g, b = color
    return (255-r, 255-g, 255-b)


def LighterColor(color, mag=1.25):
    ''' Returns opposed color.'''
    r, g, b = color
    return (min(255, int(r*mag)),
            min(255, int(g*mag)),
            min(255, int(b*mag)))


def DarkerColor(color, mag=0.75):
    ''' Returns opposed color.'''
    r, g, b = color
    return (max(0, int(r*mag)),
            max(0, int(g*mag)),
            max(0, int(b*mag)))


def GetRandomColor():
    ''' Returns random color.'''
    return (randint(0, 255), randint(0, 255), randint(0, 255))


def GetTableColor(index):
    ''' Get table color under index.'''
    return defaultColorCycler.GetColor(index)


def GetNextTableColor():
    '''
        Returns next color from predefinied
        table of example based colors.
    .'''
    global defaultColorCycler
    return defaultColorCycler.GetNextColor()
