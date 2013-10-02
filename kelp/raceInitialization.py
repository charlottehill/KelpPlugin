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

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        # initializaton - we only need to look at Green Flag scripts for Race Initialization
        scripts = {'Cat': set(), 'Rooster': set()}
        for sprite in scratch.sprites:
            if sprite.name == 'Cat' or sprite.name == 'Rooster':
                for script in sprite.scripts:
                    if not isinstance(script, kurt.Comment):
                        if KelpPlugin.script_start_type(script) == self.HAT_GREEN_FLAG:
                            scripts[sprite.name].add(script)
        
        #initialize boolean initialization variables to False
        catPos = False
        catSize = False
        roosterPos = False
        roosterOrien = False

        #access the Cat's blocks
        for script in scripts['Cat']:
            for block in script:
                # after convert() blockType is string of general category block fits into
                blockType = block.type.convert()
                if blockType.command == 'setSizeTo:':
                    if block.args[0] == 100:
                        catSize = True
                elif blockType.command == 'gotoX:y:': 
                    if block.args[0] >= 131:
                        catPos = True
        
        #access the Rooster's blocks
        for script in scripts['Rooster']:
            for block in script:
                # after convert() blockType is string of general category block fits into
                blockType = block.type.convert()
                if blockType.command == 'pointTowards:':
                    if block.args[0] == 'finish line':
                        roosterOrien = True
                elif blockType.command == 'gotoX:y:': 
                    if block.args[0] >= 131:
                        roosterPos = True

        return {'Cat': catPos and catSize, 'Rooster': roosterPos and roosterOrien}


def initialization_display(sprites):
    html = []
    if False in sprites.values():
        for name, initialized in sprites.items():
            if not initialized:
                html.append('<h2 style="background-color:LightBlue">')
                html.append('You still need to initialize the {0} sprite.'.format(name))
                html.append('<h2>')
    else:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job! You initialized all the sprites!')
        html.append('<h2>')
    return ''.join(html)

