"""This plugin is for Lesson 5: Scene Changes; Project: GoldRush."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
from . import initializationViewer
import os
import sys
import kurt


BASE_PATH = './results'

class GoldRush(KelpPlugin):

    def __init__(self):
        super(GoldRush, self).__init__()

    def checkStage(self, scripts):
        # make sure there's 6 distinct backgrounds
        costumes = set()
        initialized = False
        scene1 = False
        scene2 = False
        scene3 = False

        message1 = ''
        message2 = ''

        for script in scripts:
            background1 = False
            background2 = False
            background3 = False
            time1 = False
            time2 = False
            if not isinstance(script, kurt.Comment):
                #greenflag: check for initialization of background
                if KelpPlugin.script_start_type(script) == self.HAT_GREEN_FLAG:
                    for block in script.blocks:
                        if block.type.text == 'switch backdrop to %s':
                            costumes.add(block.args[0])
                            initialized = True
                elif KelpPlugin.script_start_type(script) == self.HAT_WHEN_I_RECEIVE:
                    if message2 == '':
                        message1 = script[0].args[0]
                    for name, _, block in self.iter_blocks(script.blocks):
                        if 'backdrop' in name:
                            if time2:
                                background3 = True
                            elif time1:
                                background2 = True
                            else:
                                background1 = True
                        if name == 'wait %s secs':
                            if background2:
                                time2 = True
                            elif background1:
                                time1 = True
                        if name == 'when I receive %s':
                            message2 = block.args[0]
                    # scene 1 and 3 only have a costume change
                    if background1 and not (background2 and background3 and time1 and time2):
                        if scene1:
                            scene3 = True
                        else:
                            scene1 = True
                    elif message2 != '':
                        scene2 = True
                        self.messages['scene2'] = message1
                        self.messages['nextbutton2'] = message2
        return initialized and scene1 and scene2 and scene3

    def checkButton(self, scripts):
        init = False
        show = False
        broadcast = False
        hide = False
        for script in scripts:
            if KelpPlugin.script_start_type(script) == self.HAT_GREEN_FLAG:
                #check for placement and show
                for block in script.blocks:
                    if block.type.text == 'show':
                        show = True
                    if block.type.text == 'go to x:%s y:%s':
                        init = True
            elif KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                for block in script.blocks:
                    if 'broadcast' in block.type.text:
                        broadcast = True
                        self.messages['scene1'] = block.args[0]
                    elif broadcast and block.type.text == 'hide':
                        hide = True
        return init and show and broadcast and hide

    def checkArrow(self, scripts, message):
        hide1 = False
        init = False
        show = False
        broadcast = False
        hide2 = False
        for script in scripts:
            if KelpPlugin.script_start_type(script) == self.HAT_GREEN_FLAG:
                for block in script.blocks:
                    if block.type.text == 'hide':
                        hide1 = True
                    elif block.type.text == 'go to x:%s y:%s':
                        init = True
            elif script[0].type.text == 'when I receive %s':
                for block in script.blocks:
                    if block.type.text == 'show':
                        show = True
            elif KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                for block in script.blocks:
                    name = block.type.text
                    if 'broadcast' in name:
                        self.messages[message] = block.args[0]
                        broadcast = True
                    elif broadcast and name == 'hide':
                        hide2 = True
        return hide1 and init and show and broadcast and hide2

    def check49er(self, scripts):
        # should have a when I receive with animation
        # should have a hide somewhere other than the gf
        hide = False
        show = False
        walk = False
        say = False
        broadcast = False

        #animation
        costume1 = False
        time1 = False
        move1 = False
        costume2 = False
        time2 =False
        move2 =False
        costume3 = False
        time3 =False
        move3 =False

        move = set()
        for (name, _) in KelpPlugin.BLOCKMAPPING['position']:
            move.add(name)

        time = set(['wait %s secs', 'glide %s secs to x:%n y:%n'])

        for script in scripts:
            if not isinstance(script, kurt.Comment):
                if KelpPlugin.script_start_type(script) == self.HAT_WHEN_I_RECEIVE:
                    for name, _, block in self.iter_blocks(script.blocks):
                        if name == 'hide':
                            hide = True
                            break
                        if name == 'show':
                            show = True
                        elif show and 'costume' in name:
                            if move2 and time2:
                                costume3 = True
                            elif move1 and time1:
                                costume2 = True
                            else:
                                costume1 = True
                        elif show and name in move:
                            if costume3:
                                move3 = True
                            elif costume2:
                                move2 = True
                            elif costume1:
                                move1 = True
                        if show and name in time:
                            if costume3:
                                time3 = True
                            elif costume2:
                                time2 = True
                            elif costume1:
                                time1 = True
                        walk = costume1 and costume2 and costume3
                        walk = walk and time1 and time2 and time3
                        walk = walk and move1 and move2 and move3
                        if walk and ('say' in name or 'think' in name):
                            say = True
                        elif say and 'broadcast' in name:
                            broadcast = True
        return walk and say and broadcast and show and hide

    def checkPan(self, scripts):
        costume = False
        say = False
        shake = False
        time1 = False
        time2 = False
        move1 = False
        move2 = False
        move = set()
        for (name, _) in KelpPlugin.BLOCKMAPPING['position']:
            move.add(name)
        for script in scripts:
            if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                for name, _, block in self.iter_blocks(script.blocks):
                    # check for movement and time?
                    if name in move:
                        if time1:
                            move2 = True
                        else:
                            move1 = True
                    if 'wait' in name:
                        if move2:
                            time2 = True
                        elif move1:
                            time1 = True
                    # check for costume change
                    if 'costume' in name:
                        costume = True
                    # check for say block
                    if costume:
                        if 'say' in name or 'think' in name:
                            say = True
        shake = time1 and time2 and move1 and move2
        return costume and say and shake

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        self.messages = {'scene1': '', 'scene2': '',
                         'scene3': '', 'nextButton': '',
                         'nextButton2': ''}
        # check that everything's initialized
        init = initializationViewer.Initialization()
        init = init.analyze(scratch)

        scenes = dict()
        required = set(['Button', 'Gold Finder',
                       'BlueArrow', 'Gold Pan', 'PurpleArrow'])

        # they need at least five sprites
        if len(scratch.sprites) < 5:
            scenes['incomplete'] = 'You have less than five sprites'
            return {'scenes': scenes, 'changes': init['changes']}

        # they can't change the sprite names
        given = set()
        for sprite in scratch.sprites:
            given.add(sprite.name)
        scenes['missing'] = required - given
        if len(scenes['missing']) > 0:
            return {'scenes': scenes, 'changes': init['changes']}
        else:
            del scenes['missing']

        # check the stage
        scenes['Stage'] = self.checkStage(scratch.stage.scripts)
        for sprite in scratch.sprites:
            if sprite.name == 'Button':
                scenes['Button'] = self.checkButton(sprite.scripts)
            elif sprite.name == 'BlueArrow':
                scenes[sprite.name] = self.checkArrow(sprite.scripts, 'Scene2')
            elif sprite.name =='PurpleArrow':
                scenes[sprite.name] = self.checkArrow(sprite.scripts, 'Scene3')
            elif sprite.name == 'Gold Finder':
                scenes[sprite.name] = self.check49er(sprite.scripts)
            elif sprite.name == 'Gold Pan':
                scenes[sprite.name] = self.checkPan(sprite.scripts)

        return {'scenes': scenes, 'changes': init['changes']}

def goldRush_display(results):
    congratulations = True
    html = []

    #initialized
    for sprite, correct in results['changes'].items():
        if not correct:
            congratulations = False
            html.append('<h2 style="background-color:LightBlue">')
            html.append('{0} still needs to be initialized.'.format(sprite))
            html.append('</h2>')


    # missing sprites?
    if 'incomplete' in results['scenes'].keys():
        html.append('<h2 style="background-color:LightBlue">')
        html.append(results['scenes']['incomplete'])
        html.append('</h2>')
        return ''.join(html)

    # renamed sprites?
    if 'missing' in results['scenes'].keys():
        for sprite in results['scenes']['missing']:
            html.append('<h2 style="background-color:LightBlue">')
            html.append('Did you rename {0}? I can\'t find it!'.format(sprite))
            html.append('</h2>')
        return ''.join(html)

    # all the sprite are there
    for sprite, correct in results['scenes'].items():
        if not correct:
            congratulations = False
            html.append('<h2 style="background-color:LightBlue">')
            html.append('Sprite {0} isn\'t done yet.'.format(sprite))
            html.append('</h2>')

    # finished
    if congratulations:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job!')
        html.append('</h2>')

    return ''.join(html)
