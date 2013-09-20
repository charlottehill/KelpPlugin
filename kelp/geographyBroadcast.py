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

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)
        # initializaton - we only need to look at Green Flag scripts for Race Initialization
        self.types = dict()
        self.types[self.HAT_MOUSE] = dict()
        self.types[self.HAT_WHEN_I_RECEIVE] = dict()
        #self.types[self.HAT_GREEN_FLAG] = dict()
        #self.types[self.NO_HAT] = dict()
        #self.types[self.HAT_KEY] = dict()
    
        # self.types dictionary now only contains 'visible' onClick & whenIReceive scripts
        
        for event in self.types.keys():
            for morph in scratch.sprites + [scratch.stage]:
                self.types[event][morph.name] = set()

        #go through the visible scripts                                                                                  
        for sprite, script in KelpPlugin.iter_sprite_visible_scripts(scratch):
            if KelpPlugin.script_start_type(script) in self.types.keys():
                self.types[KelpPlugin.script_start_type(script)][sprite].add(script)

        # dictionary which contains coordinates as values
        # the 1st tuple value is what the coordinates of the city SHOULD be
        # the 2nd tuple value is what the actual coordinates are of the city in the project turned in
        # a comparison is then done in geography_displayto see if they are in decent range of each other.

        self.spritePosition = dict()
        self.spritePosition = {unicode('Sacramento'): [(5, 98)],
                           unicode('SantaBarbara'): [(136, -144)],
                           unicode('SanFrancisco'): [(32, -49)],
                           unicode('LakeTahoe'): [(82, 108)],
                           unicode('Fresno'): [(92, 40)],
                           unicode('LosAngeles'): [(128, -70)]
                           }

        for sprite in scratch.sprites:
            if sprite.name != 'Car':
                self.spritePosition[sprite.name].append(sprite.position)

        return {'events': self.types, 'thumbnails': self.thumbnails(scratch), 'positions': self.spritePosition}

def geography_display(results):
        thumbnails = results['thumbnails']
        events = results['events']
        cityCoordinates = results['positions']


        # check to see if the city sprites are put in a reasonable location ( within 100 x/y coordinates )
        # if this is true, add boolean value of True to the cities list. It will come after the 2 coordinate pairs.
        # a dictionary entry will be of the format:
        # 'Los Angeles': [(128, -70), (132, -62), True]
        # note: the 'buffer' of allowable coordinates is set to plus or minus 100 and is easily changeable in range()

        for cities, coordinates in cityCoordinates.items():
            if coordinates[1][0] in range(coordinates[0][0]-100,coordinates[0][0]+100) and coordinates[1][1] in range(coordinates[0][1]-100,coordinates[0][1]+100):
                coordinates.append(True)
            else:
                coordinates.append(False)

        #dictionary of sprites and their broadcast messages
        # {'spriteName' : 'broadcastMessage'}
        spriteBroadcastMessages = dict()

        #dictionary of car's receive messages
        # {receiveMessage: [( command, argrument), ...]}
        carReceiveMessages = dict()

        for entries in events.values():
            for sprites in entries.items():
                if sprites[0] != 'Car':
                    for scripts in sprites[1]:
                        for blocks in scripts:
                            # after convert(), blockType is string of general category block fits into
                            blockType = blocks.type.convert()
                            if blockType.command == 'broadcast:':
                                spriteBroadcastMessages[sprites[0]] = blocks.args[0]
                else:#CAR#
                    for script in sprites[1]:
                        for block in script:
                            blockTypes = block.type.convert()
                            if blockTypes.command == 'whenIReceive':
                                receiveMessage = block.args[0]
                                carReceiveMessages[receiveMessage] = []
                            else:
                                #for arguments in block.args:
                                carReceiveMessages[receiveMessage].append((blockTypes.command,block.args))

        #list of acceptable say / think blocks
        # this list needs to be check to make sure the categories are correct
        acceptedSayThinkBlocks = ['say:duration:elapsed:from:', 'say:',
                                  'think:duration:elapsed:from', 'think:']

        dictionaryOfChecks = dict()

        # logic to see if student has correction motion and say block
        for spriteName, bcastMessage in spriteBroadcastMessages.items():
            for receiveMessage, blocks in carReceiveMessages.items():
                if bcastMessage == receiveMessage:
                    dictionaryOfChecks[spriteName] = {'motion': False, 'say': False, 'coordinates': False}
                    for commandAndArgs in blocks:
                        if commandAndArgs[0] in acceptedSayThinkBlocks:
                            sayValue = commandAndArgs[1][0]
                            sayValue = sayValue.replace(' ','')
                            if spriteName in sayValue:
                                dictionaryOfChecks[spriteName]['say'] = True
                        # manually list of acceptable motion blocks
                        if commandAndArgs[0] == 'gotoSpriteOrMouse:' and commandAndArgs[1][0] == spriteName:
                            dictionaryOfChecks[spriteName]['motion'] = True
                        elif commandAndArgs[0] == 'glideSecs:toX:y:elapsed:from:': # xy coordinate block
                            # check x and y coordinates against coordinates of where they put sprite
                            # I put these values in new variable names because the logic got tricky for the range
                            lowerXBound = cityCoordinates[spriteName][0][0] - 50
                            upperXBound = cityCoordinates[spriteName][0][0] + 50
                            lowerYBound = cityCoordinates[spriteName][0][1] - 50
                            upperYBound = cityCoordinates[spriteName][0][1] + 50
                            if commandAndArgs[1][1] in range(lowerXBound,upperXBound) and commandAndArgs[1][2] in range(lowerYBound,upperYBound):
                                dictionaryOfChecks[spriteName]['motion'] = True

        #adding coordinate booleans to dictionaryOfChecks
        for cities, coordinateBooleans in cityCoordinates.items():
            for sprites, checks in dictionaryOfChecks.items():
                if cities == sprites:
                    if coordinateBooleans[2] == True:
                        dictionaryOfChecks[sprites]['coordinates'] = True
                        
        html = []

        for cities, booleans in dictionaryOfChecks.items():
                displayHTML(cities, booleans['coordinates'], booleans['motion'], booleans['say'],html, thumbnails, True)

        # TO DO: check to see if this accounts for a broadcast with no matching receive
                
        # display incorrect broadcast / receive
        for towns in cityCoordinates.keys():
            newTowns = towns.replace(" ","")
            if newTowns not in spriteBroadcastMessages.keys():
                displayHTML(newTowns, False, False, False, html, thumbnails, False)
        
        return ''.join(html)

def displayHTML(spriteName, coordinatesBoolean, motionBoolean, sayBoolean, html, pictures, properBroadcastReceive):

    congratulations = False
    
    # if all three things are done properly
    if coordinatesBoolean and motionBoolean and sayBoolean:
        congratulations = True

    if congratulations:
        backgroundColor = 'LightGreen'
    else:
        backgroundColor = 'LightBlue'

        #this list is used to display the wrong things first
    boolDict = {'coordinatesBoolean':coordinatesBoolean, 'motionBoolean':motionBoolean, 'sayBoolean':sayBoolean}

    html.append('<h2> {0} Broadcast Double Checks </h2>'.format(spriteName))

        # Table
    html.append('<table border="1">')
    html.append('<tr>')

        #first cell
    html.append('<td style="text-align:center;">')
    html.append('{0}'.format(spriteName))
    html.append('<br>')
    html.append('<img src="{0}" height="100" width="100" style="float:center">'.format(pictures[spriteName]))
    html.append('</td>')


        #second cell
    html.append('<td style="border:none;padding-left:20px;padding-right:20px;background-color:{0}">'.format(backgroundColor))

    if congratulations:
        html.append('<h3>Congratulations! everything is correct for this sprite</h3>')
        html.append('</td>')
    else:
        html.append('<ul>')
        # print out false checks first
        for boolName, boolValue in boolDict.items():
            if boolValue == False:
                if boolName == 'coordinatesBoolean':
                    html.append('<li>')
                    html.append('The {0} sprite was NOT placed in the correct location'.format(spriteName))
                    html.append('</li>')
                if boolName == 'motionBoolean':
                    html.append('<li>')
                    html.append('The car sprite does NOT drive to {0} when {0} is clicked'.format(spriteName))
                    html.append('</li>')
                if boolName == 'sayBoolean':
                    html.append('<li>')
                    html.append('The car sprite does NOT say \"{0}\" when {0} is clicked'.format(spriteName))
                    html.append('</li>')

    #now print out correct checks
    if not congratulations:
        for boolName, boolValue in boolDict.items():
            if boolValue == True:
                html.append('<li>')
                if boolName == 'coordinatesBoolean':
                    html.append('The {0} sprite was placed in the correct location'.format(spriteName))
                if boolName == 'motionBoolean':
                    html.append('The car sprite drives to {0} when {0} is clicked'.format(spriteName))
                if boolName == 'sayBoolean':
                    html.append('The car sprite says \"{0}\" when {0} is clicked'.format(spriteName))
                html.append('</li>')
        html.append('</ul>')

        html.append('</td>')
    html.append('</tr>')
    html.append('</table>')
        
    return html

