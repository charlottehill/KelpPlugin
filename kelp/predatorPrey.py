"""This plugin is for the Predator Prey Project &  Sequence Lesson."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
import os
import sys
import kurt
import PIL
import pprint
import math

'''How to run this plugin:
kelp <project file> sequential predator
'''


class Predator(KelpPlugin):
    def __init__(self):
        super(Predator, self).__init__

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        pickedup = {'Horse': False, 'Bear': False,
                    'Snake': False, 'Zebra': False}
        # locations of all the animals
        locations = {'Horse': (128, -26), 'Bear': (51, 91),
                    'Snake': (134, -126), 'Zebra': (-143, -115)}

        # find the script we need
        script = []
        for sprite in scratch.sprites:
            if sprite.name =="Net":
                #assume there's only one script
                script = sprite.scripts[0]

        # net's position is initialized in a hidden script
        (x1, y1) = (-190, 72)
        (x2, y2) = (x1, y1)
        direction = 90

        # iterate through the script and calculate where the net goes
        for name, _, block in self.iter_blocks(script):
            if name == "point in direction %s":
                direction = block.args[0]
            elif name == "turn @turnRight %s degrees":
                direction = direction + block.args[0]
            elif name == "turn @turnLeft %s degrees":
                direction = direction - block.args[0]
            elif name == "glide %s steps":
                # calculate next location
                x2 = x1 + math.cos(direction)*block.args[0]
                y2 = y1 + math.sin(direction)*block.args[0]
                # check line
                for animal, (x3, y3) in locations.items():
                    if not pickedup[animal]:
                        #check if point3 is close to the line
                        distance = math.fabs((x2-x1)*(y1-y3)-(x1-x3)*(y2-y1))
                        denominator = (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)
                        if denominator == 0:
                            distance = 100000 #infinity
                        else:
                            distance = distance / math.sqrt(denominator)
                        #check if the distance between point3 and the line < 50
                        if distance < 50:
                            pickedup[animal] = True
                (x1, y1) = (x2, y2)

        return pickedup

def predator_display(seq):
    html = []
    negative = []
    for name, pickedup in seq.items():
        if name == 'Snake':
            if pickedup:
                negative.append('<h2 style="background-color:LightBlue">')
                negative.append('Are you sure that a snake is a mammal?')
                negative.append('</h2>')
            else:
                html.append('<h2 style="background-color:LightGreen">')
                html.append('Great job avoiding the snake!')
                html.append('</h2>')
        else:
            if pickedup:
                html.append('<h2 style="background-color:LightGreen">')
                html.append('Great job picking up the {0}!'.format(name))
                html.append('</h2>')
            else:
                negative.append('<h2 style="background-color:LightBlue">')
                negative.append('It looks like you didn\'t pick up the {0}. Is it a mammal?'.format(name))
                negative.append('</h2>')

    html.append('<br>')
    if len(negative) > 0:
        html.append('<h2>If you still have time...</h2>')
        html.extend(negative)

    return ''.join(html)
