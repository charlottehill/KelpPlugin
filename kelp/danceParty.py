"""This plugin is for Lesson 4: Costumes; Project: DanceParty."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
from . import initializationViewer
import os
import sys
import kurt


BASE_PATH = './results'

class DancePartyProject(KelpPlugin):

    def __init__(self):
        super(DancePartyProject, self).__init__()

    # each sprite has to have at least three different costume changes
    # with some sort of timing in between
    def checkDance(self, sprite):
        # names of timing blocks
        timing = set(['wait %s secs', 'glide %s secs to x:%s y:%s',
                      'say %s for %s secs', 'think %s for %s secs'])

        costume1 = False
        timing1 = False
        costume2 = False
        timing2 = False
        costume3 = False
        for script in sprite.scripts:
            if not isinstance(script, kurt.Comment):
                if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                    for name, _, block in self.iter_blocks(script):
                       # check for a costume change
                        if 'costume' in name:
                            if timing2:
                                costume3 = True
                            elif timing1:
                                costume2 = True
                            elif not costume1:
                                costume1 = True
                       # check for a timing block
                        if name in timing:
                            if costume2:
                                timing2 = True
                            elif costume1:
                                timing1 = True
        return costume1 and timing1 and costume2 and timing2 and costume3

    def analyze(self, scratch, **kwargs):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        # check initialization
        changes = dict()
        init = initializationViewer.Initialization()
        init = init.analyze(scratch)
        for sprite, attrdict in init['changes'].items():
            initialized = True
            if sprite != 'Ballerina' and sprite != 'Stage':
                for attribute in attrdict.values():
                    if len(attribute) > 0:
                        initialized = False
                changes[sprite] = initialized


        # check the sprites' dances
        dance = dict()
        for sprite in scratch.sprites:
            if sprite.name != 'Ballerina':
                dance[sprite.name] = self.checkDance(sprite)

        return {'dance': dance, 'changes': changes}

def danceProj_display(results):
    html = []
    negative = []

    # initialization
    if ('Cassy' in results['changes'].keys()) and ('CoolDude' in results['changes'].keys()):
        if results['changes']['Cassy'] and results['changes']['CoolDude']:
            html.append('<h2 style="background-color:LightGreen">')
            html.append('Great job initializing Cassy and CoolDude!</h2>')
        elif results['changes']['Cassy'] or results['changes']['CoolDude']:
            for sprite, result in results['changes'].items():
                if result:
                    html.append('<h2 style="background-color:LightGreen">')
                    html.append('Great job initializing {0}!</h2>'.format(sprite))
                else:
                    negative.append('<h2 style="background-color:LightBlue">')
                    negative.append('It looks like you still need to initialize {0}.</h2>'.format(sprite))
        else:
            negative.append('<h2 style="background-color:LightBlue">')
            negative.append('It looks like you still need to initialize Cassy and CoolDude</h2>')
    
    # dance
    if ('Cassy' in results['dance'].keys()) and ('CoolDude' in results['dance'].keys()):
        if results['dance']['Cassy'] and results['dance']['CoolDude']:
            html.append('<h2 style="background-color:LightGreen">')
            html.append('Great job making dance routines for Cassy and CoolDude!</h2>')
        elif results['dance']['Cassy'] or results['dance']['CoolDude']:
            for sprite, result in results['dance'].items():
                if result:
                    html.append('<h2 style="background-color:LightGreen">')
                    html.append('Great job making a dance routine for {0}!</h2>'.format(sprite))
                else:
                    negative.append('<h2 style="background-color:LightBlue">')
                    negative.append('It looks like {0} still needs a dance routine.</h2>'.format(sprite))
        else:
            negative.append('<h2 style="background-color:LightBlue">')
            negative.append('It looks like you still need to make dance routines for Cassy and CoolDude.</h2>')

    # finished: check bonus
    if len(negative) == 0:
        if len(html) == 0:
            negative.append('<h2 style="background-color:LightBlue">')
            negative.append('Did you rename some of the sprites?')
        else:
            if len(results['dance'].keys()) < 4:
                negative.append('<h2 style="background-color:LightBlue">')
                negative.append('Great job! All the sprites have dance routines. Try adding another sprite!')
                negative.append('</h2>')

    if len(negative) > 0:
        html.append('<br><h2>If you still have time...</h2>')
        html.extend(negative)

    return ''.join(html)
