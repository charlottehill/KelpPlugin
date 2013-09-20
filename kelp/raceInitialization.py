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
        self.types = dict()
        self.types[self.HAT_GREEN_FLAG] = dict()
        #self.types[self.NO_HAT] = dict()
        #self.types[self.HAT_WHEN_I_RECEIVE] = dict()
        #self.types[self.HAT_KEY] = dict()
    
        # self.types dictionary now only contains 'visible' Green flag scripts

        for event in self.types.keys():
            for morph in scratch.sprites + [scratch.stage]:
                self.types[event][morph.name] = set()


        #go through the visible scripts                                                                                                         
        for sprite, script in KelpPlugin.iter_sprite_visible_scripts(scratch):
            #does not include NO_HAT scripts
            if KelpPlugin.script_start_type(script) in self.types.keys():
                self.types[KelpPlugin.script_start_type(script)][sprite].add(script)

        return {'events': self.types, 'thumbnails': self.thumbnails(scratch)}

def initialization_display(results):
        thumbnails = results['thumbnails']
        events = results['events']

         # Displays sprite names and pictures                                                             

        #initialize boolean initialization variables to False
        catPositionInitialized = False
        catSizeInitialized = False
        roosterPositionInitialized = False
        roosterOrientationInitialized = False

        #initialized block values to analyze later
        catSetSizeTo = 0
        catXCoordinate = 0
        roosterOrienation = 0
        roosterXCoordinate = 0

        #access "Cat's" blocks
        for entries in events.values():
            for sprites in entries.items():
                if sprites[0] == 'Cat':
                    for scripts in sprites[1]:
                        for blocks in scripts:
                            # after convert() blockType is string of general category block fits into
                            blockType = blocks.type.convert()
                            if blockType.command == 'setSizeTo:':
                                catSetSizeTo = blocks.args[0]
                            elif blockType.command == 'gotoX:y:': 
                                catXCoordinate = blocks.args[0]
                elif sprites[0] == 'Rooster':
                    for scripts in sprites[1]:
                        for blocks in scripts:
                            # after convert() blockType is string of general category block fits into
                            blockType = blocks.type.convert()
                            if blockType.command == 'pointTowards:':
                                roosterOrientation = blocks.args[0]
                            elif blockType.command == 'gotoX:y:': 
                                roosterXCoordinate = blocks.args[0]

        #logic for determining if Cat & Rooster were initialized
        if catXCoordinate >= 131:
            catPositionInitialized = True

        if catSetSizeTo == 100:
            catSizeInitialized = True

        if roosterOrientation == 'finish line':
            roosterOrientationInitialized = True

        if roosterXCoordinate >= 131:
            roosterPositionInitialized = True
            
                    
        html = []
        displayHTML('Cat',catPositionInitialized, catSizeInitialized, html, thumbnails)
        displayHTML('Rooster',roosterPositionInitialized, roosterOrientationInitialized, html, thumbnails)
        return ''.join(html)

def displayHTML(spriteName, positionInitialized, otherSpriteInitialization, html, pictures):

    congratulations = False
    backgroundColor = 'LightBlue'

    if positionInitialized and otherSpriteInitialization:
        congratulations = True
        backgroundColor = 'LightGreen'

        html.append('<h2> {0} Initialization Table </h2>'.format(spriteName))

        # Table
        html.append('<table border="1">')
        html.append('<tr>')

        #first cell
        html.append('<td style="text-align:center;">')
        html.append('{0}'.format(spriteName))
        html.append('<br>')
        html.append('<img src="{0}" height="100" width="100" style="float:center;">'.format(pictures[spriteName]))
        html.append('</td>')

        #second cell
        html.append('<td style="border:none;padding-left:20px;padding-right:20px;background-color:{0};">'.format(backgroundColor))

    if congratulations == True:
        html.append('<h3>')
        html.append('Congratulations! Everything was initialized correctly for the {0}'.format(spriteName))
        html.append('</h3>')
    else:
        if positionInitialized == False or otherSpriteInitialization == False:
            html.append('<h3>')
            html.append('You forgot to initialize the {0}'.format(spriteName))
            html.append('</h3>')

    html.append('</td>')
    html.append('</tr>')
    html.append('</table>')
        
    return html

