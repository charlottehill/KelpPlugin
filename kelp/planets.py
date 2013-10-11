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

    # returns a boolean 
    # true if the planet's say bubble is correct, false otherwise
    def checkPlanet(self, sprite):
        correct = False
        for script in sprite.scripts:
            # check scripts that start with 'when sprite clicked'
            if not isinstance(script, kurt.Comment):
                if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                    for name, _, block in self.iter_blocks(script):
                        # find the say blocks
                        if 'say' in name or 'think' in name:
                            # check to see if it says the sprite's name
                            if sprite.name.lower() in block.args[0].lower():
                                correct = True
                                break
        return correct

    # returns a boolean
    # true if the rocket is correct, false otherwise
    def checkRocket(self, scratch):
        rocket = False
        for sprite in scratch.sprites:
            if sprite.name == 'Rocket':
                rocket = sprite
        # if there's not a rocket sprite, return false
        if not rocket:
            return False

        # check the visible scripts
        # there should be scripts for right, left and down
        left = False
        right = False
        down = False
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
                left = True
            if move and key == 'right arrow' and direction == 90:
                right = True
            if move and key == 'down arrow' and direction == 180:
                down = True
        if left and right and down:
            return True
        else:
            return False

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        planets = dict()
        for sprite in scratch.sprites:
            if sprite.name != 'Rocket' and sprite.name != 'Sun':
                # check that it was named correctly
                if sprite.name.lower() == sprite.costumes[0].name.lower():
                    name = True
                else:
                    name = False
                # check the name and say bubble
                planets[sprite.name] = (name, self.checkPlanet(sprite))

        rocket = self.checkRocket(scratch)
        return {'planets': planets, 'rocket': rocket}


def planetProj_display(results):
    html = []
    noerrors = True

    # check the rocket
    if not results['rocket']:
        noerrors = False
        html.append('<h2 style="background-color:LightBlue">')
        html.append('The rocket isn\'t done.')
        html.append('<h2>')

    # check the planet
    for planet, (name, say) in results['planets'].items():
        if not name and not say:
            noerrors = False
            html.append('<h2 style="background-color:LightBlue">')
            html.append('{0} isn\'t named correctly and it doesn\'t say its name when clicked.'.format(planet))
            html.append('<h2>')
        elif not name:
            noerrors = False
            html.append('<h2 style="background-color:LightBlue">')
            html.append('{0} isn\'t named correctly.'.format(planet))
            html.append('<h2>')
        elif not say:
            noerrors = False
            html.append('<h2 style="background-color:LightBlue">')
            html.append('{0} doesn\'t say its name when clicked.'.format(planet))
            html.append('<h2>')

    # check if there weren't any errors
    if noerrors:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job! The rocket and all the planets are finished!')
        html.append('<h2>')

    return ''.join(html)
