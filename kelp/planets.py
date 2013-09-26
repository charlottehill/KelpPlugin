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

    def checkSpriteName(self,scratch):

        self.costumes = set()

        for sprite in scratch.sprites:
            for costume in sprite.costumes:
                if costume.name.lower() != sprite.name.lower():
                    self.costumes.add(sprite)
        return self.costumes

    def checkSayThink(self, scratch):

        #initialize
        self.types = dict()
        for morph in scratch.sprites:
            self.types[morph.name] = set()

        #go through the visible scripts and add the sprites with a say or think block that contain the sprite's name
        for sprite, script in KelpPlugin.iter_sprite_visible_scripts(scratch):
            if script.reachable:
                if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                    for name, _, block in self.iter_blocks(script):
                        if 'say' in name or 'think' in name:
                            if sprite.lower() in block.args[0].lower():
                                self.types[sprite].add(script)
                                break

        #pprint.pprint(self.types)

        #if a sprite has no say or think block, their project isn't complete
        noSay = set()
        for sprite in self.types.keys():
            if sprite != 'Rocket':
                if sprite != 'Sun':
                    if not self.types[sprite]:
                        noSay.add(sprite)

        #return list of sprites without a say or think block
        return noSay

    def checkRocket(self, scratch):

        #make a dictionary to only look at Rocket Scripts
        # that start with 'When Key Pressed' Hat Blocks
        self.types = dict()
        self.types[self.HAT_KEY] = dict()

        for event in self.types.keys():
            for morph in scratch.sprites:
                    self.types[event][morph.name] = set()

        for sprite, script in KelpPlugin.iter_sprite_visible_scripts(scratch):
            if KelpPlugin.script_start_type(script) in self.types.keys():
                self.types[KelpPlugin.script_start_type(script)][sprite].add(script)

        return self.types[self.HAT_KEY]

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        return {'no say': self.checkSayThink(scratch), 'sprite names': self.checkSpriteName(scratch), 'rocket blocks': self.checkRocket(scratch), 'thumbnails': self.thumbnails(scratch)}




def planetProj_display(results):

    noSay = results['no say']
    spriteNames = results['sprite names']
    pictures = results['thumbnails']
    rocketBlocks = results['rocket blocks']

    rocketDict = {'left arrow': {'heading': False, 'forward': False},
                  'right arrow': {'heading': False, 'forward': False},
                  'down arrow': {'heading': False, 'forward': False},
                  'up arrow': {'heading': False, 'forward': False}
                  }

    whichBlock = 'left arrow'

    #rocket's logic
    for sprites, sets in rocketBlocks.items():
        if sprites == 'Rocket':
            for scripts in sets:
                for blocks in scripts:
                    blockType = blocks.type.convert()
                    if blockType.command == 'whenKeyPressed':
                        if blocks.args[0] == 'left arrow':
                            whichBlock = 'left arrow'
                        if blocks.args[0] == 'right arrow':
                            whichBlock = 'right arrow'
                        if blocks.args[0] == 'up arrow':
                            whichBlock = 'up arrow'
                        if blocks.args[0] == 'down arrow':
                            whichBlock = 'down arrow'
                    elif blockType.command == 'heading:':
                        if whichBlock == 'left arrow' and blocks.args[0] == -90:
                            rocketDict['left arrow']['heading'] = True
                        elif whichBlock == 'right arrow' and blocks.args[0] == 90:
                            rocketDict['right arrow']['heading'] = True
                        elif whichBlock == 'up arrow' and blocks.args[0] == -180:
                            rocketDict['up arrow']['heading'] = True
                        elif whichBlock == 'down arrow' and blocks.args[0] == 180:
                            rocketDict['down arrow']['heading'] = True
                    elif blockType.command == 'forward:':
                        if whichBlock == 'left arrow' and blocks.args[0] >= 1:
                            rocketDict['left arrow']['forward'] = True
                        elif whichBlock == 'right arrow' and blocks.args[0] >= 1:
                            rocketDict['right arrow']['forward'] = True
                        elif whichBlock == 'up arrow' and blocks.args[0] >= 1:
                            rocketDict['up arrow']['forward'] = True
                        elif whichBlock == 'down arrow' and blocks.args[0] >= 1:
                            rocketDict['down arrow']['forward'] = True

    #print('ROCKET DICT')
    #pprint.pprint(rocketDict)

    #print('rocketBlocks')
    #pprint.pprint(rocketBlocks)

    backgroundColor = 'LightBlue'

    html = []

    rocketCongratulations = False

    for arrows, characteristics in rocketDict.items():
        #print('boolean')
        #print(characteristics['forward'])
        for titles, booleans in characteristics.items():
            if booleans == False:
                rocketCongratulations = False
                break
            elif booleans == True:
                rocketCongratulations = True


    spriteCongratulations =  not noSay and not spriteNames

    if rocketCongratulations:
        backgroundColor = 'LightGreen'

    html.append('<h2> Rocket  Double Check </h2>')

        # Table
    html.append('<table border="1">')
    html.append('<tr>')

        #first cell
    html.append('<td style="text-align:center;">')
    html.append('Rocket')
    html.append('<br>')
    html.append('<img src="{0}" height="100" width="100" style="float:center;">'.format(pictures['Rocket']))
    html.append('</td>')


    #second cell
    html.append('<td style="border:none;padding-left:20px;padding-right:20px;background-color:{0}">'.format(backgroundColor))
    if rocketCongratulations:
        html.append('<h3>Congratulations! This sprite is correct<h3>')
    else:
        html.append('<h3>This sprite still needs some work</h3>')

    html.append('</td>')

    html.append('</tr>')
    html.append('</table>')

    backgroundColor = 'LightBlue'

    if spriteCongratulations:
        backgroundColor = 'LightGreen'

    for spriteName in rocketBlocks.keys():
        if spriteName!= 'Rocket':
            html.append('<h2> {0}  Double Check </h2>'.format(spriteName))

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
            html.append('<td style="border:none;padding-left:20px;padding-right:20px;background-color:{0}">'.format(backgroundColor))
            if spriteCongratulations:
                html.append('<h3>Congratulations! This sprite is correct<h3>')
            else:
                html.append('<h3>This sprite still needs some work</h3>')

            html.append('</td>')

            html.append('</tr>')
            html.append('</table>')

    return ''.join(html)
