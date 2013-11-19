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
        return planets


def planetProj_display(results):
    html = []
    negative = []

    # check the planet
    for planet, correct in results.items():
        if correct:
            html.append('<h2 style="background-color:LightGreen">')
            html.append('Great job making {0} say its name when clicked!'.format(planet))
            html.append('<h2>')
        else:
            negative.append('<h2 style="background-color:LightBlue">')
            negative.append('It looks like {0} doesn\'t say its name when clicked.'.format(planet))
            negative.append('<h2>')

    html.append('<br>')
    if len(negative) > 0:
        html.append('<h2>If you still have time...</h2>')
        html.extend(negative)

    return ''.join(html)
