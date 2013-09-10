"""This plugin is for Lesson 2: Events; Project: Planets."""

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
                if costume.name != sprite.name:
                    self.costumes.add(sprite)
        return self.costumes
    
    def checkSayThink(self, scratch):
        
        #initialize
        self.types = dict()
        for morph in scratch.sprites:
            self.types[morph.name] = set()
        
        #go through the visible scripts and add the sprite with a say or think block
        for sprite, script in KelpPlugin.iter_sprite_visible_scripts(scratch):
            if script.reachable:
                if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                    for name, _, block in self.iter_blocks(script):
                        if 'say' in name or 'think' in name:
                            self.types[sprite].add(script)
                            break

        #if a sprite has no say or think block, their project isn't complete
        noSay = set()
        for sprite in self.types.keys():
            if sprite != 'Rocket':
                if sprite != 'Sun':
                    if not self.types[sprite]:
                        noSay.add(sprite)
    
        #return list of sprites without a say or think block
        return noSay

    '''def checkRocket(self, scratch):
        
        #initialize
        self.typesR = set()
        
        #go through the visible scripts and add the sprite with a say or think block
        for sprite, script in KelpPlugin.iter_sprite_visible_scripts(scratch):
            if script.reachable:
                if sprite.name == 'Rocket':
                    if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                        for name, _, block in self.iter_blocks(script):
                            if 'say' in name or 'think' in name:
                                self.types[sprite].add(script)
                                break'''

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)
            
        return {'no say': self.checkSayThink(scratch), 'sprite names': self.checkSpriteName(scratch)}

def planetProj_display(results):
    
    noSay = results['no say']
    spriteNames = results['sprite names']
    
    html = []
    if not noSay:
        html.append('Your sprites say their names, good job!')
    else:
        for sprite in noSay:
            html.append('Make sure {0} says its name!'.format(sprite))

    if not spriteNames:
        html.append('Nice job naming all your sprites correctly!')
    else:
        html.append('Make sure you name all your sprites correctly!')

    print(html)
    
    return ''.join(html)