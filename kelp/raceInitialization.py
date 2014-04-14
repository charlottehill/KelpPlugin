"""This plugin is for the Race Initialization project."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
import os
import sys
import kurt

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


class raceInitialization(KelpPlugin):

    def __init__(self):
        super(raceInitialization, self).__init__()

        """Returns a dictionary of the scripts.
        Keys: start events
        Values: another dictionary
        Keys: sprite names
        Values: that sprite's scripts for this start event ."""

    def analyze(self, scratch, **kwargs):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        # initializaton - we only need to look at Green Flag scripts for Race Initialization
        # look at when clicked to see if they initialize after clicking
        scripts = {'Cat': set(), 'Rooster': set()}
        scriptsClicked = {'Cat': set(), 'Rooster': set()}
        for sprite in scratch.sprites:
            if sprite.name == 'Cat' or sprite.name == 'Rooster':
                for script in sprite.scripts:
                    if not isinstance(script, kurt.Comment):
                        if KelpPlugin.script_start_type(script) == self.HAT_GREEN_FLAG:
                            scripts[sprite.name].add(script)
                        elif "when this sprite clicked" in script.blocks[0].stringify():
                            scriptsClicked[sprite.name].add(script)

        #initialize boolean initialization variables to False
        catPos = False
        catSize = False
        roosterPos = False
        roosterOrien = False
        roosterSet = False
        catSet = False

        #for clicked
        catPos2 = False
        catSize2 = False
        roosterPos2 = False
        roosterOrien2 = False
        roosterSet2 = False
        catSet2 = False

        #access the Cat's blocks
        for script in scripts['Cat']:
            for block in script:
                if block.type.text == 'set size to %s%%':
                    if block.args[0] == 100:
                        catSize = True
                elif block.type.text == 'go to x:%s y:%s':
                    if block.args[0] >= 145:
                        catPos = True
                elif block.type.text == 'set x to %s':
                    if block.args[0] >= 145:
                        if catSet: # already set y
                            catPos = True
                        else:
                            catSet = True
                elif block.type.text == 'set y to %s':
                    if catSet: # already set x
                        catPos = True
                    else:
                        catSet = True
        #access to cat clicked
        for script in scriptsClicked['Cat']:
            for block in script:
                if block.type.text == 'set size to %s%%':
                    if block.args[0] == 100:
                        catSize2 = True
                elif block.type.text == 'go to x:%s y:%s':
                    if block.args[0] >= 145:
                        catPos2 = True
                elif block.type.text == 'set x to %s':
                    if block.args[0] >= 145:
                        if catSet: # already set y
                            catPos2 = True
                        else:
                            catSet2 = True
                elif block.type.text == 'set y to %s':
                    if catSet: # already set x
                        catPos2 = True
                    else:
                        catSet2 = True
        
        #access the Rooster's blocks
        for script in scripts['Rooster']:
            for block in script:
                if block.type.text == 'point towards %s':
                    if block.args[0] == 'finish line':
                        roosterOrien = True
                elif block.type.text == 'point in direction %s':
                	if block.args[0] == -90:
                		roosterOrien = True
                elif block.type.text == 'go to x:%s y:%s':
                    if block.args[0] >= 145:
                        roosterPos = True
                elif block.type.text == 'set x to %s':
                    if block.args[0] >= 145:
                        if roosterSet: # already set y
                            roosterPos = True
                        else:
                            roosterSet = True
                elif block.type.text == 'set y to %s':
                    if roosterSet: # already set x
                        roosterPos = True
                    else:
                        roosterSet = True
        #access the Rooster clicked
        for script in scriptsClicked['Rooster']:
            for block in script:
                if block.type.text == 'point towards %s':
                    if block.args[0] == 'finish line':
                        roosterOrien2 = True
                elif block.type.text == 'point in direction %s':
                	if block.args[0] == -90:
                		roosterOrien2 = True
                elif block.type.text == 'go to x:%s y:%s':
                    if block.args[0] >= 145:
                        roosterPos2 = True
                elif block.type.text == 'set x to %s':
                    if block.args[0] >= 145:
                        if roosterSet: # already set y
                            roosterPos2 = True
                        else:
                            roosterSet2 = True
                elif block.type.text == 'set y to %s':
                    if roosterSet: # already set x
                        roosterPos = True
                    else:
                        roosterSet = True
        return {'Cat': catPos and catSize, 'Rooster': roosterPos and roosterOrien,
                'CatClicked': catPos2 and catSize2,'RoosterClicked': roosterPos2 and roosterOrien2  }


def initialization_display(sprites):
    
    html = []
    negative = ['<h2 style="background-color:LightBlue">']
    if sprites['Cat'] and sprites['Rooster']:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job initializing the rooster and the cat!</h2>')
    elif not sprites['Cat'] and not sprites['Rooster']:
        negative.append('It looks like you still need to initialize the rooster and the cat.')
        if sprites['CatClicked'] and sprites['RoosterClicked']:
            negative.append('\nIt looks like you initialized the rooster and the cat after they moved but not when the green flag is clicked.')
    else:
        for name, initialized in sprites.items():
            if name == 'CatClicked' or name == 'RoosterClicked':
                continue
            if not initialized:
                negative.append('It looks like you still need to initialize the {0}.'.format(name))
                if sprites[name + 'Clicked']:
                    negative.append('\nIt looks like you initialized the {0} after it moved but not when the green flag is clicked.'.format(name))
            else:
                html.append('<h2 style="background-color:LightGreen">')
                html.append('Great job initializing the {0}!</h2>'.format(name))

    if len(negative) > 1:
        negative.append('</h2>')
        html.append('<br><h2>If you still have time...</h2>')
        html.extend(negative)

    return ''.join(html)

