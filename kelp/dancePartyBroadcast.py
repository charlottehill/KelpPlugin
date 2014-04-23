"""This plugin is for Lesson 4: Costumes; Project: DanceParty."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
from . import initializationViewer
import os
import sys
import kurt


BASE_PATH = './results'

class DancePartyProjectBR(KelpPlugin):

    def __init__(self):
        super(DancePartyProjectBR, self).__init__()

    # checking to see whether dancing starts via broadcast/receive or not
    def checkBroadcast(self, sprite):
    	flag = False  #boolean to tell whether this sprite had broadcast/receive in it
        for script in sprite.scripts:
        	for block in script.blocks:
        		if 'broadcast' in block.stringify() or 'receive' in block.stringify():
        			flag = True
        return flag
        			 
    def analyze(self, scratch, **kwargs):
    	spriteBR = dict() #keyvalue pair for each sprite telling whether broadcast/receive
    					  #was used or not
    	for sprite in scratch.sprites:
    		spriteBR[sprite.name] = self.checkBroadcast(sprite)
    	
    	return spriteBR
        
def danceProj_display(results):
    html = []
    negative = []
    for key,pair in results.items():
		if pair:
			html.append('<h2 style="background-color:LightGreen">')
			html.append(key + ' used broadcast/receive</h2>')
		else:
			html.append('<h2 style="background-color:Yellow">')
			html.append(key + ' did NOT use broadcast/receive</h2>')
    return ''.join(html)
