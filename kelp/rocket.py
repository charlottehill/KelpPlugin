"""This plugin is for Lesson 2: Events; Project: Planets."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
import os
import sys
import kurt
import pprint

'''How to run this plugin:
    hairball -k <path>/octopi.py -d <folder where sequenceViewer is> -p sequenceViewer.Sequence test.sb
    For example, if `octopi.py` and sequenceViewer are both in the directory where you are:
    hairball -k octopi.py -d . -p sequenceViewer.Sequence test.sb
    if sequenceViewer is in your directory but octopi.py is right outside of it:
    hairball -k ../octopi.py -d . -p sequenceViewer.Sequence test.sb
    If they're both right outside of it:
    hairball -k ../octopi.py -d .. -p sequenceViewer.Sequence test.sb
'''

BASE_PATH = './results'

class Rocket(KelpPlugin):

    def __init__(self):
        super(Rocket, self).__init__()

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        blocks = {'left': False, 'right': False, 'down': False}
        for sprite in scratch.sprites:
            if sprite.name == 'Rocket':
                rocket = sprite
        # if there's not a rocket sprite, return false
        if not rocket:
            return blocks

        # check the visible scripts
        # there should be scripts for right, left and down
        for script in rocket.scripts:
            key = ''
            direction = ''
            move = False
            if not isinstance(script, kurt.Comment):
                for name, _, block in self.iter_blocks(script):
                    if name == 'when %s key pressed':
                        key = block.args[0]
                    if name == 'point in direction %s':
                        direction = block.args[0]
                    if 'steps' in name and block.args[0] > 0:
                        move = True
            if move and key == 'left arrow' and direction == -90:
                blocks["left"] = True
            if move and key == 'right arrow' and direction == 90:
                blocks["right"] = True
            if move and key == 'down arrow' and direction == 180:
                blocks["down"] = True
        return blocks

def rocket_display(results):
    html = []
    negative = []

    for block, correct in results.items():
        if correct:
            html.append('<h2 style="background-color:LightGreen">')
            html.append('Great job making the rocket go {0}!'.format(block))
            html.append('<h2>')
        else:
            negative.append('<h2 style="background-color:LightBlue">')
            negative.append('It looks like the rocket doesn\'t go {0} when the {0} arrow key is pressed.'.format(block))
            negative.append('<h2>')

    if len(negative) != 0:
        html.append('<br>')
        html.extend(negative)

    return ''.join(html)
