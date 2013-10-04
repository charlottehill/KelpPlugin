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
    # coordinates = 
    def car(self, scripts, messages, coordinates):
        sprites = {'SantaBarbara': 'Santa Barbara',
                   'LosAngeles': 'Los Angeles',
                   'LakeTahoe': 'Lake Tahoe',
                   'Fresno': 'Fresno',
                   'Sacramento': 'Sacramento',
                   'SanFrancisco': 'San Francisco'}

        lat = {'SantaBarbara': '119w', 'LosAngeles': '118w',
               'LakeTahoe': '119w', 'Fresno': '119w',
               'Sacramento': '121w', 'SanFrancisco': '122w'}

        long = {'SantaBarbara': '34n', 'LosAngeles': '34n',
                'LakeTahoe': '39n', 'Fresno': '37n',
                'Sacramento': '39n', 'SanFrancisco': '37n'}

        # does the car dive to these cities?
        drive = {'Santa Barbara': False, 'Los Angeles': False,
                 'Lake Tahoe': False, 'Fresno': False,
                 'Sacramento': False, 'San Francisco': False}

        # does the car say the city's name and position?
        say = {'Santa Barbara': False, 'Los Angeles':False,
              'Lake Tahoe': False, 'Fresno':False,
                 'Sacramento': False, 'San Francisco': False}

        for script in scripts:
            # check for the message in the broadcasted messages dict
            print(script[0].args[0])
            if script[0].args[0] in messages:
                city = messages[script[0].args[0]]
                for name, _, block in self.iter_blocks(script.blocks):
                    # check say block for name, latitude and longitude
                    if 'say' in name:
                        bubble = block.args[0].lower()
                        if sprites[city].lower() in bubble:
                            if lat[city] in bubble:
                                if long[city] in bubble:
                                    say[sprites[city]] = True
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
                        print(block.args[1], block.args[2])
                        print(coordinates[city])
                        if abs(block.args[1] - coordinates[city][0]) <= 50:
                            if abs(block.args[2] - coordinates[city][1]) <=50:
                                drive[sprites[city]] = True
        return drive, say


    def analyze(self, scratch):
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

    congratulations = True
    html = []

    # does the car say each city's name and location?
    for city, correct in results['say'].items():
        if not correct:
            congratulations = False
            html.append('<h2 style="background-color:LightBlue">')
            html.append('The car doesn\'t say {0}\'s name and location when {0} is clicked.'.format(city))
            html.append('<h2>')

    # does the car drive to each city?
    for city, correct in results['drive'].items():
        if not correct:
            congratulations = False
            html.append('<h2 style="background-color:LightBlue">')
            html.append('The car doesn\'t go to {0} when {0} is clicked.'.format(city))
            html.append('<h2>')

    # if all three things are done properly
    if congratulations:
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job! The car goes to all the cities and says their names!')
        html.append('<h2>')

    return ''.join(html)

