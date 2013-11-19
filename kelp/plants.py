"""This plugin is for Lesson 5: Scene Changes; Project: GoldRush."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
from . import initializationViewer
import os
import sys
import kurt


BASE_PATH = './results'

class Plants(KelpPlugin):

    def __init__(self):
        super(Plants, self).__init__()


    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        scenes = {'renamed':False,
                  'initialized': {'Stage':False, 'Cloud':False, 'Sun':False, 'Button':False},
                  'raining': {'show': False, 'background': False},
                  'sunny': {'show': False, 'hide': False, 'background': False}}

        sprites = {'green flag':dict(), 'receive':dict(), 'clicked':dict()}
        for sprite in scratch.sprites + [scratch.stage]:
            if sprite.name not in scenes['initialized'].keys():
                return {'renamed': True}
            for category in sprites.keys():
                sprites[category][sprite.name] = set()
            for script in sprite.scripts:
                if not isinstance(script, kurt.Comment):
                    if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                        sprites['clicked'][sprite.name].add(script)
                    elif KelpPlugin.script_start_type(script) == self.HAT_GREEN_FLAG:
                        sprites['green flag'][sprite.name].add(script)
                    elif KelpPlugin.script_start_type(script) == self.HAT_WHEN_I_RECEIVE:
                        sprites['receive'][sprite.name].add(script)
                    
        #check green flag?


        # check cloud clicked
        costume = False
        broadcast = False
        for script in sprites['clicked']['Cloud']:
            for name, _, block in self.iter_blocks(script):
                if name == 'switch costume to %s' and block.args[0] == 'Raining':
                    costume = True
                if costume and name == 'broadcast %s':
                    broadcast = block.args[0]
                    break
        #check raining
        if broadcast:
            # the button should show
            for script in sprites['receive']['Button']:
                if script[0].args[0] == broadcast:
                    for name, _, block in self.iter_blocks(script):
                        if name == 'show':
                            scenes['raining']['show'] = True
            # the stage should switch to background Sapling
            for script in sprites['receive']['Stage']:
                if script[0].args[0] == broadcast:
                    for name, _, block in self.iter_blocks(script):
                        if name == 'switch costume to %s' and block.args[0] == 'Sapling':
                            scenes['raining']['background'] = True

        # check button clicked
        hide = False
        broadcast = False
        for script in sprites['clicked']['Button']:
            for name, _, block in self.iter_blocks(script):
                if name == 'hide':
                    hide = True
                if hide and name == 'broadcast %s':
                    broadcast = block.args[0]
                    break
        #check sunny
        if broadcast:
            hide = True
            # the sun should show
            # the cloud should hide
            # the stage should switch to background Flower
            

        return hide

def plant_display(results):
    html = []
    negative = []

#scenes = {'renamed':False, 'initialized': {'Stage':False, 'Cloud':False, 'Sun':False, 'Button':False},
#                  'raining': {'show': False, 'background': False},
#                  'sunny': {'show': False, 'hide': False, 'background': False

    # renamed sprites?
    if results['renamed']:
        html.append('<h2 style="background-color:LightBlue">')
        html.append('Did you rename some of the sprites?</h2>')
        return ''.join(html)

    #initialized
    for sprite, correct in results['initialized'].items():
        if correct:
            html.append('<h2 style="background-color:LightGreen">')
            html.append('Great job initializing {0}!'.format(sprite))
            html.append('</h2>')
        else:
            negative.append('<h2 style="background-color:LightBlue">')
            negative.append('It looks like {0} still needs to be initialized.'.format(sprite))
            negative.append('</h2>')



    html.append('<br>')
    if len(negative) > 0:
        html.append('<h2>If you still have time...</h2>')
        html.extend(negative)

    return ''.join(html)
