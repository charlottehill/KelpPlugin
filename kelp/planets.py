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

class PlanetsProject(KelpPlugin):

    def __init__(self):
        super(PlanetsProject, self).__init__()

    def checkRocket(self, rocket):
        blocks = {'left': False, 'right': False, 'down': False}

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



    def checkApprox(self, actual, name):
        if name[0] == actual[0]:
            if actual == 'mercury':
                if ('y' in name) or ('e' in name):
                    return True
            elif actual == 'mars':
                if 'a' in name:
                    return True
            else:
                return True
        else:
            return False

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)


        # check rocket: if there's not a rocket sprite, return false 
        rocket = False
        for sprite in scratch.sprites:
            if sprite.name == 'Rocket':
                rocket = sprite
        if rocket:
            blocks = self.checkRocket(rocket)
        else:
            blocks = {'left': False, 'right': False, 'down': False}

        planets = {'Mercury': False, 'Venus': False,
                       'Earth': False, 'Mars': False,
                       'Jupiter': False, 'Saturn': False,
                       'Uranus': False, 'Neptune': False}
        for sprite in scratch.sprites:
            name = sprite.costumes[0].name.encode('ascii','ignore')
            if name != 'Rocket' and name != 'Sun':
                # check the name and say bubble
                for script in sprite.scripts:
                    # check scripts that start with 'when sprite clicked'
                    if not isinstance(script, kurt.Comment):
                        if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                            for blockname, _, block in self.iter_blocks(script):
                                # find the say blocks
                                if 'say' in blockname or 'think' in blockname:
                                    # check to see if it says the sprite's name
                                    if self.checkApprox(name.lower(), block.args[0].lower().encode('ascii','ignore')):
                                        planets[name] = True
        return {'rocket': blocks, 'planets': planets}


def planetProj_display(results):
    html = []
    correct = []
    incorrect = []

    #planets
    for planet, say in results['planets'].items():
        if say:
            correct.append(planet)
        else:
            incorrect.append(planet)

    if len(incorrect) == 0: #all correct
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making all the planets say their names when clicked!</h2>')
    elif len(correct) == 0: #all incorrect
        html.append('<h2 style="background-color:LightBlue">')
        html.append('It looks like the planets don\'t say their names when clicked.</h2>')
    else: #some correct and some incorrect
        html.append('<h2 style="background-color:LightGreen">Great job making {0}'.format(correct[0]))
        if len(correct) == 1: #one correct and the rest are incorrect
            html.append(' say its name when clicked!</h2>')
        else:
            for n in range(len(correct)-2):
                html.append(', {0}'.format(correct[n+1]))
            html.append(' and {0} say their names when you click them!</h2>'.format(correct[-1]))
        html.append('<h2>If you still have time...</h2>')
        html.append('<h2 style="background-color:LightBlue">It looks like {0}'.format(incorrect[0]))
        if len(incorrect) == 1: #one is incorrect and the rest are correct
            html.append(' doesn\'t say its name when clicked.</h2>')
        else:
            for n in range(len(incorrect)-2):
                html.append(', {0}'.format(incorrect[n+1]))
            html.append(' and {0} don\'t say their names when you click them.</h2>'.format(incorrect[-1]))


    #rocket
    correct = []
    incorrect = []
    for block, dir in results['rocket'].items():
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
         html.append('<h2 style="background-color:LightBlue">')
         html.append('It looks like the rocket still needs some work!</h2>')
    # 2 correct, 1 incorrect
    elif len(correct) == 2:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making the rocket move {0} and {1}!</h2>'.format(correct[0], correct[1]))
        html.append('<h2>If you still have time...</h2>')
        html.append('<h2 style="background-color:LightBlue">')
        html.append('It looks like the rocket doesn\'t go {0}</h2>'.format(incorrect[0]))
    # 1 correct, 2 incorrect
    else:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making the rocket move {0}!</h2>'.format(correct[0]))
        html.append('<h2>If you still have time...</h2>')
        html.append('<h2 style="background-color:LightBlue">')
        html.append('It looks like the rocket doesn\'t go {0} or {1}</h2>'.format(incorrect[0], incorrect[1]))

    return ''.join(html)
