'''
Created on 23 lis 2020

@author: spasz
'''

from random import randint

white = (255, 255, 255)
darkgray = (64, 64, 64)
gray = (128, 128, 128)
lightgray = (192, 192, 192)
black = (0, 0, 0)
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
pink = (0, 255, 255)
cyan = (255, 255, 0)
magenta = (255, 0, 255)


def GetRandomColor():
    ''' Returns random color.'''
    return (randint(0, 255), randint(0, 255), randint(0, 255))
