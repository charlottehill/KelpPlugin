"""This plugin is for the Predator Prey Project &  Sequence Lesson."""

from __future__ import print_function
from kelpplugin import KelpPlugin
import math

'''How to run this plugin:
kelp <project file> sequential predator
'''


class Predator(KelpPlugin):
    def __init__(self):
        super(Predator, self).__init__

    def analyze(self, scratch, **kwargs):
        pickedup = {'Horse': False, 'Bear': False,
                    'Snake': False, 'Zebra': False}
        # locations of all the animals
        locations = {'Horse': (128, -26), 'Bear': (51, 91),
                     'Snake': (134, -126), 'Zebra': (-143, -115)}

        # find the script we need
        script = []
        for sprite in scratch.sprites:
            if sprite.name == 'Net':
                # assert len(sprite.scripts) == 1
                script = sprite.scripts[0]  # assume there's only one script

        # net's position is initialized in a hidden script
        x1, y1 = -190, 72
        x2, y2 = x1, y1
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
                rad = math.radians(direction)
                x2 = x1 + math.sin(rad)*block.args[0]
                y2 = y1 + math.cos(rad)*block.args[0]
                # check line
                for animal, (x3, y3) in locations.items():
                    if not pickedup[animal]:
                        # find the distance between the point and line segment
                        px = x2 - x1
                        py = y2 - y1
                        something = float(px*px + py*py)
                        u = ((x3 - x1) * px + (y3 - y1) * py) / something
                        if u > 1:
                            u = 1
                        elif u < 0:
                            u = 0
                        dx = x1 + u * px - x3
                        dy = y1 + u * py - y3
                        distance = math.sqrt(dx*dx + dy*dy)
                        # check if the distance between point and the line < 70
                        if distance < 70:
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
                negative.append('Are you sure that a snake is a mammal?</h2>')
            else:
                html.append('<h2 style="background-color:LightGreen">')
                html.append('Great job avoiding the snake!</h2>')
        else:
            if pickedup:
                html.append('<h2 style="background-color:LightGreen">')
                html.append('Great job picking up the {0}!</h2>'.format(name))
            else:
                negative.append('<h2 style="background-color:LightBlue">')
                negative.append('It looks like you didn\'t pick up the {0}. Is'
                                ' it a mammal?</h2>'.format(name))

    html.append('<br>')
    if len(negative) > 0:
        html.append('<h2>If you still have time...</h2>')
        html.extend(negative)
    else:
        html = []
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job picking up all the mammals!</h2>')

    return ''.join(html)
