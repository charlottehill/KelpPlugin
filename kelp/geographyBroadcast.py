"""This plugin is for the CAGeographyBroadcast project."""

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


class geographyBroadcast(KelpPlugin):

    def __init__(self):
        super(geographyBroadcast, self).__init__()

        """Returns a dictionary of the scripts.                                                
        Keys: start events                                                                     
        Values: another dictionary                                                             
        Keys: sprite names                                                                     
        Values: that sprite's scripts for this start event ."""

    # sprites = car's when I receive scripts
    # messages = dictionary
    # messages[city sprite name] = sprite's broadcast message
    # coordinates = sprites' locations
    def car(self, scripts, messages, coordinates):
        sprites = {'SantaBarbara': 'Santa Barbara',
                   'LosAngeles': 'Los Angeles',
                   'LakeTahoe': 'Lake Tahoe',
                   'Fresno': 'Fresno',
                   'Sacramento': 'Sacramento',
                   'SanFrancisco': 'San Francisco'}

        # does the car dive to these cities?
        drive = {'Santa Barbara': False, 'Los Angeles': False,
                 'Lake Tahoe': False, 'Fresno': False,
                 'Sacramento': False, 'San Francisco': False}

        # does the car say the city's name and position?
        say = {'Santa Barbara': 2, 'Los Angeles':2,
              'Lake Tahoe': 2, 'Fresno':2,
                 'Sacramento': 2, 'San Francisco': 2}

        for script in scripts:
            # check for the message in the broadcasted messages dict
            if script[0].args[0] in messages:
                city = messages[script[0].args[0]]
                for name, _, block in self.iter_blocks(script.blocks):
                    # check say block for name, latitude and longitude
                    if 'say' in name:
                        bubble = block.args[0].lower()
                        if sprites[city].lower() in bubble:
                            say[sprites[city]] = 0
                        else:
                            if bubble[0] == 's':
                                if 'b' in bubble:
                                    say['Santa Barbara'] = 1
                                elif 'f' in bubble:
                                    say['San Francisco'] = 1
                                else:
                                    say['Sacramento'] = 1
                            elif bubble[0] =='l':
                                if 'lake' in bubble:
                                    say['Lake Tahoe'] = 1
                                elif 'a' in bubble:
                                    say['Los Angeles'] = 1
                            elif bubble[0] == 'f':
                                say['Fresno'] = 1
                                                        
                    # check go to block
                    elif 'go to %s' in name:
                        if city in block.args[0]:
                            drive[sprites[city]] = True
                    # use the other sprite's coordinates (in coordinates dictionary)
                    elif 'go to x:%s y:%s' in name:
                        if abs(block.args[0] - coordinates[city][0]) <= 50:
                            if abs(block.args[1] - coordinates[city][1]) <=50:
                                drive[sprites[city]] = True
                    elif 'glide %s secs to x:%s y:%s' in name:
                        if abs(block.args[1] - coordinates[city][0]) <= 50:
                            if abs(block.args[2] - coordinates[city][1]) <=50:
                                drive[sprites[city]] = True
        return drive, say


    def analyze(self, scratch, **kwargs):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        # record the car's When I Receive scripts
        # and the cities' When Clicked scripts
        sprite_scripts = dict()
        sprite_scripts['Car'] = set()
        for sprite in scratch.sprites:
            sprite_scripts[sprite.name] = set()
            for script in sprite.scripts:
                if not isinstance(script, kurt.Comment):
                    if sprite.name == 'Car':
                        if KelpPlugin.script_start_type(script) == self.HAT_WHEN_I_RECEIVE:
                            sprite_scripts[sprite.name].add(script)
                    else:
                        if KelpPlugin.script_start_type(script) == self.HAT_MOUSE:
                            sprite_scripts[sprite.name].add(script)

        # record the messages broadcasted by the cities
        messages = dict()
        for sprite, scripts in sprite_scripts.items():
            if sprite != 'Car':
                for script in scripts:
                    for name, _, block in self.iter_blocks(script.blocks):
                        if 'broadcast' in name:
                            messages[block.args[0]] = sprite

        # record the coordinates of the city sprites
        coordinates = dict()
        for sprite in scratch.sprites:
            if sprite.name != 'Car':
                coordinates[sprite.name] = sprite.position

        # check the car
        test = sprite_scripts['Car']
        drive, say = self.car(sprite_scripts['Car'], messages, coordinates)

        return {'drive': drive, 'say': say}

def geography_display(results):
    html = []
    correct = []
    spelling = []
    incorrect = []

    # does the car say each city's name?
    html.append('<h1>Part 1: Make the car say each of the cities\' names</h1>')
    for city, say in results['say'].items():
        if say == 0:
            correct.append(city)
        elif say == 1:
            spelling.append(city)
        else:
            incorrect.append(city)

    if len(incorrect) == 0 and len(correct) == 0: # all misspelled
        html.append('<h2 style="background-color:LightBlue">')
        html.append('Great job making the car say all the cities\' names!')
        html.append(' It looks like you spelled the cities incorrectly.')
        html.append(' If you have time, try checking your spelling.</h2>')
    elif len(incorrect) == 0 and len(spelling) == 0: #all correct
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making the car say all the cities\' names!</h2>')
    elif len(correct) == 0 and len(spelling) == 0: #all incorrect
        html.append('<h2 style="background-color:LightBlue">')
        html.append('It looks like the the car doesn\'t say the cities\' names when you click them.</h2>')
    else: #some correct, some incorrect and some misspelled
        if len(correct) != 0:
            html.append('<h2 style="background-color:LightGreen">Great job making the car say {0}'.format(correct[0]))
            if len(correct) == 1: #one correct and the rest are incorrect/misspelled
                html.append(' when it\'s clicked!</h2>')
            else:
                for n in range(len(correct)-2):
                    html.append(', {0}'.format(correct[n+1]))
                html.append(' and {0} when they\'re clicked!</h2>'.format(correct[-1]))
        if len(incorrect) != 0:
            html.append('<h2>If you still have time...</h2>')
            html.append('<h2 style="background-color:LightBlue">It looks like the car doesn\'t say {0}'.format(incorrect[0]))
            if len(incorrect) == 1:
                html.append(' when it\'s clicked.</h2>')
            else:
                for n in range(len(incorrect)-2):
                    html.append(', {0}'.format(incorrect[n+1]))
                html.append(' and {0} when you click them.</h2>'.format(incorrect[-1]))
        if len(spelling) != 0:
            html.append('<h2 style="background-color:LightBlue">It looks like you spelled {0}'.format(spelling[0]))
            if len(spelling) == 1:
                html.append('incorrectly</h2>')
            else:
                for n in range(len(spelling)-2):
                    html.append(', {0}'.format(spelling[n+1]))
                html.append(' and {0} incorrectly.</h2>'.format(spelling[-1]))

    # does the car drive to each city? 
    html.append('<h1><br>Part 2: Make the car drive to each of the cities</h1>')
    correct = []
    incorrect = []
    for city, drive in results['drive'].items():
        if drive:
            correct.append(city)
        else:
            incorrect.append(city)

    if len(incorrect) == 0: # all correct
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job making the car drive to all the cities!</h2>')
    elif len(correct) == 0: # all incorrect
        html.append('<h2 style="background-color:LightBlue">')
        html.append('It looks like the the car doesn\'t drive to the cities when you click them.</h2>')
    else: # some correct and some incorrect
        if len(correct) != 0:
            html.append('<h2 style="background-color:LightGreen">Great job making the car drive to {0}'.format(correct[0]))
            if len(correct) == 1: #one correct and the rest are incorrect
                html.append(' when you click on it!</h2>')
            else:
                for n in range(len(correct)-2):
                    html.append(', {0}'.format(correct[n+1]))
                html.append(' and {0} when they\'re clicked!</h2>'.format(correct[-1]))
        if len(incorrect) != 0:
            html.append('<h2>If you still have time...</h2>')
            html.append('<h2 style="background-color:LightBlue">It looks like the car doesn\'t drive to {0}'.format(incorrect[0]))
            if len(incorrect) == 1:
                html.append(' when it\'s clicked.</h2>')
            else:
                for n in range(len(incorrect)-2):
                    html.append(', {0}'.format(incorrect[n+1]))
                html.append(' and {0} when you click them.</h2>'.format(incorrect[-1]))
            
    return ''.join(html)

