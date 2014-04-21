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


    def analyze(self, scratch, **kwargs):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        scenes = {'renamed':False,
                  'initialized': {'Sun':False, 'Button':False},
                  'raining': {'show': False, 'background': False},
                  'sunny': {'show': False, 'hide': False, 'background': False},
                  'clicked': False}

        sprites = {'green flag':dict(), 'receive':dict(), 'clicked':dict()}
        for sprite in scratch.sprites + [scratch.stage]:
            if sprite.name not in ['Sun', 'Stage', 'Button', 'Cloud']:
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
                    
        #check green flag for the sun and the button
        # the sun should start with ClickMeCostume costume
        for script in sprites['green flag']['Sun']:
             for name, _, block in self.iter_blocks(script):
                 if name == 'switch costume to %s' and block.args[0] == 'ClickMeCostume':
                     scenes['initialized']['Sun'] = True
        # the button should hide
        for script in sprites['green flag']['Button']:
            for name, _, block in self.iter_blocks(script):
                if name == 'hide':
                    scenes['initialized']['Button'] = True

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
                        if name == 'switch backdrop to %s' and block.args[0] == 'Sapling':
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
            # the stage should switch to background Flower
            for script in sprites['receive']['Stage']:
                for name, _, block in self.iter_blocks(script):
                    if name == 'switch backdrop to %s' and block.args[0] == 'Flower':
                        scenes['sunny']['background'] = True
            # the sun should show
            for script in sprites['receive']['Sun']:
                for name, _, block in self.iter_blocks(script):
                    if name == 'show':
                        scenes['sunny']['show'] = True
            # the cloud should hide
            for script in sprites['receive']['Cloud']:
                for name, _, block in self.iter_blocks(script):
                    if name == 'hide':
                        scenes['sunny']['hide'] = True

        # check sun clicked
        for script in sprites['clicked']['Sun']:
            for name, _, block in self.iter_blocks(script):
                if name == 'switch costume to %s' and block.args[0] == 'Rays':
                    scenes['clicked'] = True


        return scenes

def plant_display(results):
    html = []
    negative = []

    # renamed sprites?
    if results['renamed']:
        html.append('<h2 style="background-color:LightBlue">')
        html.append('Did you rename some of the sprites?</h2>')
        return ''.join(html)

    #initialized
    if results['initialized']['Sun'] and results['initialized']['Button']:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job initializing the sun and the button!</h2>')
    elif results['initialized']['Sun']:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job initializing the sun!</h2>')
        negative.append('<h2 style="background-color:LightBlue">')
        negative.append('It looks like you still need to initialize the button.</h2>')
    elif results['initialized']['Button']:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job initializing the button!</h2>')
        negative.append('<h2 style="background-color:LightBlue">')
        negative.append('It looks like you still need to initialize the sun.</h2>')
    else:
        negative.append('<h2 style="background-color:LightBlue">')
        negative.append('It looks like you still need to initialize the button and the sun.</h2>')

    #raining
    if results['raining']['background'] and results['raining']['show']:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job changing the stage and making the button show in the rain scene!</h2>') 
    elif results['raining']['background']:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job changing the stage in the rain scene!</h2>')
        negative.append('<h2 style="background-color:LightBlue">')
        negative.append('It looks like the button doesn\t show up after it rains.</h2>')
    elif results['raining']['show']:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making the button show after it rains!</h2>')
        negative.append('<h2 style="background-color:LightBlue">')
        negative.append('It looks like the stage doesn\'t change in the rain scene.</h2>')
    else:
        negative.append('<h2 style="background-color:LightBlue">')
        negative.append('It looks like you still need to do the rain scene.</h2>')

    #sunny
    if results['sunny']['hide']:
        if results['sunny']['show'] and results['sunny']['background']: # stage and sun and hide
            html.append('<h2 style="background-color:LightGreen">')
            html.append('Great job changing the stage, making the cloud hide ')
            html.append('and making the sun show in the sunny scene!</h2>')
        elif results['sunny']['background']: # stage and hide
            html.append('<h2 style="background-color:LightGreen">')
            html.append('Great job changing the stage and making the cloud hide in the sunny scene!</h2>')
            negative.append('<h2 style="background-color:LightBlue">')
            negative.append('It looks like the Sun doesn\'t show in the sunny scene.</h2>')
        elif results['sunny']['show']: # sun and hide
            html.append('<h2 style="background-color:LightGreen">')
            html.append('Great job making the sun show and the cloud hide in the sunny scene!</h2>')
            negative.append('<h2 style="background-color:LightBlue">')
            negative.append('It looks like the stage doesn\'t change in the sunny scene.</h2>')
        else: # hide only
            html.append('<h2 style="background-color:LightGreen">')
            html.append('Great job making the cloud hide in the sunny scene!</h2>')
            negative.append('<h2 style="background-color:LightBlue">')
            negative.append('It looks like the stage doesn\'t change and the')
            negative.append(' sun doesn\'t show in the sunny scene.</h2>')
    else:
         if results['sunny']['show'] and results['sunny']['background']: # stage and sun
             html.append('<h2 style="background-color:LightGreen">')
             html.append('Great job changing the stage and making the sun show in the sunny scene!</h2>')
             negative.append('<h2 style="background-color:LightBlue">')
             negative.append('It looks like the cloud doesn\'t hide in the sunny scene.</h2>') 
         elif results['sunny']['background']: # stage only
             html.append('<h2 style="background-color:LightGreen">')
             html.append('Great job changing the stage in the sunny scene!</h2>')
             negative.append('<h2 style="background-color:LightBlue">')
             negative.append('It looks like the sun doesn\'t show and the cloud ')
             negative.append('doesn\'t hide in the sunny scene.</h2>')
         elif results['sunny']['show']: # sun
             html.append('<h2 style="background-color:LightGreen">')
             html.append('Great job making the sun show and the cloud hide in the sunny scene!</h2>')
             negative.append('<h2 style="background-color:LightBlue">')
             negative.append('It looks like the stage doesn\'t change and the')
             negative.append(' cloud doesn\'t hide in the sunny scene.</h2>')             
         else: #none
             negative.append('<h2 style="background-color:LightBlue">')
             negative.append('It looks like you still need to do the sunny scene.</h2>')

    if results['clicked']:
         html.append('<h2 style="background-color:LightGreen">')
         html.append('Great job making the sun shine when you click on it!</h2>')
    else:
         negative.append('<h2 style="background-color:LightBlue">')
         negative.append('It looks like the sun doesn\'t shine when you click on it.</h2>')

    if len(negative) > 0:
        html.append('<br><h2>If you still have time...</h2>')
        html.extend(negative)

    return ''.join(html)
