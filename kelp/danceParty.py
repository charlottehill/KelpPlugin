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
                        print(name)
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

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        # check initialization TO DO: is this working?
        init = initializationViewer.Initialization()
        init = init.analyze(scratch)

        # check the sprites' dances
        dance = dict()
        for sprite in scratch.sprites:
            dance[sprite.name] = self.checkDance(sprite)

        return {'dance': dance, 'changes': init['changes']}

def danceProj_display(results):
    congratulations = True
    html = []

    # initialization
    for sprite, correct in results['changes'].items():
        if not correct:
            congratulations = False
            html.append('<h2 style="background-color:LightBlue">')
            html.append('{0} still needs to be initialized.'.format(sprite))
            html.append('</h2>')

    # dance
    for sprite, correct in results['dance'].items():
        if not correct:
            congratulations = False
            html.append('<h2 style="background-color:LightBlue">')
            html.append('{0} doesn\'t have a complete dance routine.'.format(sprite))
            html.append('</h2>')

    # finished
    if congratulations:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job! All the sprites have dance routines.')
        html.append('</h2>')

    #bonus
    if len(results['dance'].keys()) < 4:
        html.append('<h2 style="background-color:LightBlue">')
        html.append('Try adding another sprite!')
        html.append('</h2>')

    return ''.join(html)
