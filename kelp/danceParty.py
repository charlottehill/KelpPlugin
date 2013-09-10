"""This plugin is for Lesson 4: Costumes; Project: DanceParty."""

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

class DancePartyProject(KelpPlugin):
    
    STATE_NOT_MODIFIED = 0
    STATE_MODIFIED = 1
    STATE_INITIALIZED = 2
    
    def __init__(self):
        super(DancePartyProject, self).__init__()
    
    def checkDance(self, scratch):
        
        #initialize
        self.types = dict()
        for morph in scratch.sprites:
            self.types[morph.name] = set()
        
        #go through the visible scripts and add the sprite with a costume change
        for sprite, script in KelpPlugin.iter_sprite_visible_scripts(scratch):
            if script.reachable:
                if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                    for name, _, block in self.iter_blocks(script):
                        if 'costume' in name:
                            self.types[sprite].add(script)
                            break

        #if the sprite has no costume changes, it's dance isn't complete
        noDance = set()
        for sprite in self.types.keys():
            if not self.types[sprite]:
                noDance.add(sprite)
    
        #return list of sprites with an incomplete dance
        return noDance

    def checkInitialization(self, scratch, sprite, scripts, attribute):
        """Return the state of the scripts for the given attribute.
            
            If there is more than one `when green flag clicked` script and they
            both modify the attribute, then the attribute is considered to not be
            initialized.
            
            """
        
        green_flag, other = partition_scripts(scripts, self.HAT_GREEN_FLAG)
        block_set = KelpPlugin.BLOCKMAPPING[attribute]
        state = self.STATE_NOT_MODIFIED
        # TODO: Any regular broadcast blocks encountered in the initialization
        # zone should be added to this loop for conflict checking.
        for script in green_flag:
            in_zone = True
            for name, level, block in self.iter_blocks(script.blocks):
                if name == 'broadcast %e and wait':
                    # TODO: Follow the broadcast and wait scripts that occur in
                    # the initialization zone
                    in_zone = False
                if (name, 'absolute') in block_set:
                    #print(name)
                    if in_zone and level == 0: # Success!
                        if state == self.STATE_NOT_MODIFIED:
                            state = self.STATE_INITIALIZED
                        else: # Multiple when green flag clicked conflict
                            state = self.STATE_MODIFIED
                            #self.changes[sprite][attribute].append((block, script))
                            self.uninit_attr[sprite].add(attribute)
                    elif in_zone:
                        continue # Conservative ignore for nested absolutes
                    else:
                        state = self.STATE_MODIFIED
                        #self.changes[sprite][attribute].append((block, script))
                        self.uninit_attr[sprite].add(attribute)
                    break # The state of the script has been determined
                elif (name, 'relative') in block_set:
                    state = self.STATE_MODIFIED
                    #self.changes[sprite][attribute].append((block, script))
                    self.uninit_attr[sprite].add(attribute)
                    break
        if state != self.STATE_NOT_MODIFIED:
            return state
        # Check the other scripts to see if the attribute was ever modified
        for script in other:
            for name, _, block in self.iter_blocks(script.blocks):
                if name in [x[0] for x in block_set]:
                    #self.changes[sprite][attribute].append((block, script))
                    self.uninit_attr[sprite].add(attribute)
                    state = self.STATE_MODIFIED
            
        return self.uninit_attr

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)
        
        self.sprites = set()
        
        self.uninit_attr = dict()
        for morph in scratch.sprites:
            self.uninit_attr[morph.name] = set()
            self.sprites.add(morph.name)

        for sprite in scratch.sprites + [scratch.stage]:
            for attr in self.BLOCKMAPPING.keys():
                #self.changes[sprite.name][attr] = []
                self.checkInitialization(scratch, sprite.name, sprite.scripts, attr)
            
        return {'no dance': self.checkDance(scratch), 'changes': self.uninit_attr, 'sprites': self.sprites}

def danceProj_display(results):
    
    noDance = results['no dance']
    uninit_attr = results['changes']
    sprites = results['sprites']
    
    html = []
    if not noDance:
        html.append('Your dances look great! Nice job!')
    else:
        for sprite in noDance:
            html.append("Make sure you change {0}'s costume!".format(sprite))

    if not uninit_attr:
        html.append('Good job initilizing your sprites!')
    else:
        for sprite in uninit_attr:
            html.append('Make sure you initilize {0}!'.format(sprite))

    if len(sprites) < 4:
        html.append('Make sure you add a new sprite!')
    else:
        html.append('Nice job adding a new sprite!')

    print(html)
    
    return ''.join(html)