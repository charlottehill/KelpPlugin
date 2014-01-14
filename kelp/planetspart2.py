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

def partition_scripts(scripts, start_type):
    """Return two lists of scripts out of the original `scripts` list.

        Scripts that begin with a `start_type` block are returned first. All other
        scripts are returned second.

        """
    match, other = [], []
    for script in scripts:
        if KelpPlugin.script_start_type(script) == start_type:
            match.append(script)
        else:
            other.append(script)
    return match, other

class PlanetsProjectPart2(KelpPlugin):

    def __init__(self):
        super(PlanetsProjectPart2, self).__init__()

    # return 0 if the name is spelled correctly
    # return 1 if the name is spelled incorrectly
    # return 2 if the name is wrong
    def checkApprox(self, actual, name):
        if name == actual:
            return 0
        if name[0] == actual[0]:
            if actual == 'mercury':
                if ('y' in name) or ('e' in name):
                    return 1
            elif actual == 'mars':
                if 'a' in name:
                    return 1
            else:
                return 1
        else:
            return 2

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        # check rocket: if there's not a rocket sprite, return false 
        rocket = False
        for sprite in scratch.sprites:
            if sprite.name == 'Rocket':
                rocket = sprite
        
        # there should be scripts for right, left and down 
        blocks = {'left': False, 'right': False, 'down': False}

        if rocket:
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


def planetProj_display(results):
    html = []
    negative = []
    correct = []
    spelling = []
    incorrect = []

    negative.append('<h2>If you still have time...</h2>')

    for block, dir in results.items():
        if dir:
            correct.append(block)
        else:
            incorrect.append(block)

    # all correct
    if len(correct) == 3:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making the rocket move in all directions!</h2>')
    # all incorrect
    elif len(incorrect) == 3:
         negative.append('<h2 style="background-color:LightBlue">')
         negative.append('It looks like the rocket still needs some work!</h2>')
    # 2 correct, 1 incorrect
    elif len(correct) == 2:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making the rocket move {0} and {1}!</h2>'.format(correct[0], correct[1]))
        negative.append('<h2 style="background-color:LightBlue">')
        negative.append('It looks like the rocket doesn\'t go {0}</h2>'.format(incorrect[0]))
    # 1 correct, 2 incorrect
    else:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making the rocket move {0}!</h2>'.format(correct[0]))
        negative.append('<h2 style="background-color:LightBlue">')
        negative.append('It looks like the rocket doesn\'t go {0} or {1}</h2>'.format(incorrect[0], incorrect[1]))

    if len(negative) > 1:
        html.extend(negative)

    return ''.join(html)
