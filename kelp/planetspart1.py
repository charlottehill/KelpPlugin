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

class PlanetsProjectPart1(KelpPlugin):

    def __init__(self):
        super(PlanetsProjectPart1, self).__init__()

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

    def analyze(self, scratch, **kwargs):
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
                                    planets[name] =  self.checkApprox(name.lower(), block.args[0].lower().encode('ascii','ignore'))
        return planets


def planetProj_display(results):
    html = []
    negative = []
    correct = []
    spelling = []
    incorrect = []

    negative.append('<h2>If you still have time...</h2>')

    for planet, say in results.items():
        if say == 0:
            correct.append(planet)
        elif say == 1:
            spelling.append(planet)
        else:
            incorrect.append(planet)

    if len(incorrect) == 0 and len(correct) == 0: # all misspelled
        html.append('<h2 style="background-color:LightBlue">')
        html.append('Great job making all the planets say their names when clicked!')
        negative.append(' It looks like you spelled the planets incorrectly. If you have time, try checking your spelling.</h2>')
    elif len(incorrect) == 0 and len(spelling) == 0: #all correct
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making all the planets say their names when clicked!</h2>')
    elif len(correct) == 0 and len(spelling) == 0: #all incorrect
        negative.append('<h2 style="background-color:LightBlue">')
        negative.append('It looks like the planets don\'t say their names when clicked.</h2>')
    else: #some correct and some incorrect and some misspelled
        if len(correct) != 0:
            html.append('<h2 style="background-color:LightGreen">Great job making {0}'.format(correct[0]))
            if len(correct) == 1: #one correct and the rest are incorrect/misspelled
                html.append(' say its name when clicked!</h2>')
            else:
                for n in range(len(correct)-2):
                    html.append(', {0}'.format(correct[n+1]))
                html.append(' and {0} say their names when you click them!</h2>'.format(correct[-1]))
        if len(incorrect) != 0:
            negative.append('<h2 style="background-color:LightBlue">It looks like {0}'.format(incorrect[0]))
            if len(incorrect) == 1: #one is incorrect and the rest are correct/misspelled
                negative.append(' doesn\'t say its name when clicked.</h2>')
            else:
                for n in range(len(incorrect)-2):
                    html.append(', {0}'.format(incorrect[n+1]))
                html.append(' and {0} don\'t say their names when you click them.</h2>'.format(incorrect[-1]))
        if len(spelling) != 0:
            negative.append('<h2 style="background-color:LightBlue">It looks like you spelled {0}'.format(spelling[0]))
            if len(spelling) == 1:
                negative.append('incorrectly</h2>')
            else:
                for n in range(len(spelling)-2):
                    negative.append(', {0}'.format(spelling[n+1]))
                negative.append(' and {0} incorrectly.</h2>'.format(spelling[-1]))


    if len(negative) > 1:
        html.extend(negative)

    return ''.join(html)
