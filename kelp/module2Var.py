"""This plugin is for Module 2: Events; Project: Variables."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
import os
import sys
import kurt
import PIL
import pprint
import math

'''How to run this plugin:
    hairball -k <path>/octopi.py -d <folder where sequenceViewer is> -p sequenceViewer.Sequence test.sb
    For example, if `octopi.py` and sequenceViewer are both in the directory where you are:
    hairball -k octopi.py -d . -p sequenceViewer.Sequence test.sb
    if sequenceViewer is in your directory but octopi.py is right outside of it:
    hairball -k ../octopi.py -d . -p sequenceViewer.Sequence test.sb
    If they're both right outside of it:
    hairball -k ../octopi.py -d .. -p sequenceViewer.Sequence test.sb
'''
def stringContains (string, array):
    result = 1
    for text in array:
        if not text in string:
            result = 0
    return result

def scriptContains (script, twoDarray):
    result = 0
    for block in script.blocks:
        for array in twoDarray:
            if (stringContains (block.stringify(), array)):
                result = 1
                break
    return result

class Module2Var(KelpPlugin):

    def __init__(self):
        super(Module2Var, self).__init__()

    def checkCat(self, cat):
        blocks = {'initialize var': False, 'increment var': False, 'broadcast': False}
        # check the visible scripts for the blocks
        for script in cat.scripts:
            if not isinstance(script, kurt.Comment):
                #check for initializing
                if (stringContains(script.blocks[0].stringify(), ["greenFlag"])):
                    if scriptContains(script, [["set","0"]]):
                        blocks["initialize var"] = True
                #check the pressed block
                elif (stringContains(script.blocks[0].stringify(), ["when this sprite clicked"])
                    or stringContains(script.blocks[0].stringify(), ["pressed"])):
                    if scriptContains(script, [["+","1"]]):
                        blocks["increment var"] = True
                    if scriptContains(script, [["broadcast"]]):
                        blocks["broadcast"] = True
        return blocks
    def checkMouse(self, mouse):
        blocks = {'initialize hide': False, 'receive block': False,
                  'show block': False,'move block': False,'hide block': False }
        # check the visible scripts for the blocks
        for script in mouse.scripts:
            if not isinstance(script, kurt.Comment):
                #check for initializing hide
                if (stringContains(script.blocks[0].stringify(), ["greenFlag"])):
                    if scriptContains(script, [["hide"]]):
                        blocks["initialize hide"] = True
                #check the receive block
                elif (stringContains(script.blocks[0].stringify(), ["I receive"])):
                    blocks["receive block"] = True
                    if scriptContains(script, ["show"]):
                        blocks["show block"] = True
                    if (blocks["show block"] and
                        scriptContains(script, [["move"],["glide"],["go to"]])):
                        blocks["move block"] = True
                    if (blocks["show block"] and blocks["move block"]
                        and scriptContains(script, ["hide"])):
                        blocks["hide block"] = True
        return blocks
    
    def checkDog(self, dog):
        blocks = {'initialize times hit': False, 'contains loop': False,
                  'loop ending condition': False,'move the dog': False,
                  'touching mouse': False, 'increment': False }
        # check the visible scripts for the blocks
        for script in dog.scripts:
            if not isinstance(script, kurt.Comment):
                #check for initializing
                if (stringContains(script.blocks[0].stringify(), ["greenFlag"])):
                    if scriptContains(script, [["set", "0"]]):
                        blocks["initialize times hit"] = True
                    if scriptContains(script, [["forever"], ["repeat"]]):
                        blocks["contains loop"] = True
                    if scriptContains(script, [["=","3"]]):
                        blocks["loop ending condition"] = True
                    if scriptContains(script, [["move"],["glide"],["go to"]]):
                        blocks["move the dog"] = True
                    if scriptContains(script, [["if", "touching","mouse"]]):
                        blocks["touching mouse"] = True
                    if scriptContains(script, [["+", "1"]]):
                        blocks["increment"] = True
        return blocks
    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        # check cat: if there's not a cat sprite, return false 
        cat,dog,mouse = False, False, False
        for sprite in scratch.sprites:
            if sprite.name.lower() == 'cat':
                cat = sprite
            elif sprite.name.lower() == 'dog':
                dog = sprite
            elif sprite.name.lower() == 'mouse':
                mouse = sprite 
        if cat:
            catBlocks = self.checkCat(cat)
        else:
            catBlocks = {'initialize var': False, 'increment var': False, 'broadcast': False}
        if mouse:
            mouseBlocks = self.checkMouse(mouse)
        else:
            mouseBlocks = {'initialize hide': False, 'receive block': False,
                  'show block': False,'move block': False,'hide block': False }
        if dog:
            dogBlocks = self.checkDog(dog)
        else:
            dogBlocks = {'initialize times hit': False, 'contains loop': False,
                  'loop ending condition': False,'move the dog': False,
                  'touching mouse': False, 'increment': False }
        return {'cat': catBlocks, 'mouse': mouseBlocks, 'dog' : dogBlocks}
#end class definition
def Module2VarView(mydictionary):
        html = '<h2 style="background-color:LightBlue">Module 2 variables</h2>'
        keys = mydictionary.keys()
        for key in keys:
            minidic = mydictionary[key]
            html += '<h3 style="background-color:LightBlue">' + key + '</h3>'
            minikeys = minidic.keys()
            for minikey in minikeys:
                if minidic[minikey]:
                    html += '<h4 style="background-color:LightGreen">' + minikey + ' succeed</h4>'
                else:
                    html += '<h4 style="background-color:Red">' + minikey + ' failed</h4>'
	return html



