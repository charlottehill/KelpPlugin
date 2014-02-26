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
'''
List of tests to check whether the module is correct:
cat:
1.initialize variable to 0
2.has a variable that is incremented each time when clicked of space is pressed
3.broadcast to mouse
dog:
1. initialize variable to 0
2. initialize position
3. loop that makes it bounce
4. checking if hitting mouse
5. increment variable by 1 when hit
mouse:
1.show
2. move
3. hide

Also check that the mouse can hit the dog!!
'''
twoDMouseArray = False
mouseXYDir = [False,False,False]
twoDDogArray = False
dogXYDir = [False,False,False]
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
    def loopAllInBlock(self, block,twoDArray, curXYDir):
        for argument in block.args:
            if isinstance (argument, (list,tuple)):
                    for blockInLoop in argument:
                        self.arrayDoStuff(blockInLoop.stringify(), blockInLoop,twoDArray, curXYDir)
    def convertConditionArgument(self,arg, curXYDir):
        if (isinstance (arg, str)):
            if ('x' in arg):
                arg = curXYDir[0]
            elif ('y' in arg):
                arg = curXYDir[1]
            elif ('direction' in arg):
                arg = curXYDir[2]
        return (float)(arg)
    def arrayDoStuff(self,name, block,twoDArray, curXYDir):
        if stringContains(name, ['turn', 'degrees']):
            curXYDir[2] += block.args[0]
        elif stringContains(name, ['point in direction']):
            curXYDir[2] = block.args[0]
        elif ('glide' in name or 'move' in name):
            deltaX = block.args[0] * math.sin(curXYDir[2]*math.pi/180)
            deltaY = block.args[0] * math.cos(curXYDir[2]*math.pi/180)
            #print ((str)(deltaX) + " " + (str)(deltaY))
            slope = deltaY/deltaX
            slopeY = deltaX/deltaY
            #x stuff
            sign = 1
            x = curXYDir[0]
            y = curXYDir[1]
            i = 0
            j = deltaX
            if deltaX < 0:
                sign = -1
                i = deltaX
                j = 0
            while i < j:
                xPos = round(x + 250)
                yPos = round(y + 200)
                if (xPos < 500 and yPos < 400):
                    twoDArray[(int)(xPos)][(int)(yPos)] = 1
                x = x + sign
                y = y + slope
                i += 1
            #y stuff
            sign = 1
            x = curXYDir[0]
            y = curXYDir[1]
            i = 0
            j = deltaY
            if deltaY < 0:
                sign = -1
                i = deltaY
                j = 0
            while i < j:
                xPos = round(x + 250)
                yPos = round(y + 200)
                if (xPos < 500 and yPos < 400):
                    twoDArray[(int)(xPos)][(int)(yPos)] = 1
                x = x + slopeY
                y = y + sign
                i += 1
            curXYDir[0] = curXYDir[0] + deltaX
            curXYDir[1] = curXYDir[1] + deltaY
        elif ((not 'go to front' in name) and 'go to' in name):
            curXYDir[0] = block.args[0]
            curXYDir[1] = block.args[1]
            xPos = round(curXYDir[0] + 250)
            yPos = round(curXYDir[1] + 200)
            if (xPos < 500 and yPos < 400):
                twoDArray[(int)(xPos)][(int)(yPos)] = 1
        elif name == 'if on edge, bounce':
            if (curXYDir[0] >= 237 or curXYDir[0] <= -237 or curXYDir[1] >= 177 or curXYDir[1] <= -177):
                curXYDir[2] = 360 - curXYDir[2]
            if curXYDir[0] >= 237:
                curXYDir[0] = 236
            if curXYDir[0] <= -237:
                curXYDir[0] = -236
            if curXYDir[1] >= 177:
                curXYDir[1] = 176
            if curXYDir[1] <= -177:
                curXYDir[1] = -176
        elif stringContains(name, ["if"]):
            if block.args and len(block.args) > 0:
                condition = block.args[0].stringify()
                if isinstance(block.args[0], kurt.Block) and block.args[0].args and len(block.args[0].args) >= 2:
                    if '=' in condition:
                        firstCase = self.convertConditionArgument(block.args[0].args[0], curXYDir)
                        secondCase = self.convertConditionArgument(block.args[0].args[1], curXYDir)
                        if (firstCase == secondCase):
                            self.loopAllInBlock(block,twoDArray,curXYDir)
                    elif '<' in condition:
                        firstCase = self.convertConditionArgument(block.args[0].args[0], curXYDir)
                        secondCase = self.convertConditionArgument(block.args[0].args[1], curXYDir)
                        if (firstCase < secondCase):
                            self.loopAllInBlock(block,twoDArray,curXYDir)
                    elif '>' in condition:
                        firstCase = self.convertConditionArgument(block.args[0].args[0], curXYDir)
                        secondCase = self.convertConditionArgument(block.args[0].args[1], curXYDir)
                        if (firstCase > secondCase):
                            self.loopAllInBlock(block,twoDArray,curXYDir)
        elif stringContains(name, ["forever"]) or stringContains(name, ["repeat"]):
            #do the loop 1000 times just to make sure all the cases covered
            count = 0
            while count < 1000:
                self.loopAllInBlock(block, twoDArray, curXYDir)
                count += 1
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
    def doMouseInitializeBlock(self,script, blocks):
        global twoDMouseArray
        global mouseXYDir
        if scriptContains(script, [["hide"]]):
            blocks["initialize hide"] = True
            for name, _, block in self.iter_blocks(script):
                if name == 'go to x:%s y:%s':
                    mouseXYDir[0] = block.args[0]
                    mouseXYDir[1] = block.args[1]
                    twoDMouseArray[mouseXYDir[0] + 250][mouseXYDir[1] + 200] = 1
                if name == 'point in direction %s':
                    mouseXYDir[2] = block.args[0]
    def doMouseReceiveBlock(self,script, blocks):
        global twoDMouseArray
        global mouseXYDir
        for name, _, block in self.iter_blocks(script):
            if name == 'show':
                blocks["show block"] = True
            elif name == 'hide' and blocks["show block"]:
                blocks["hide block"] = True
            else:
                self.arrayDoStuff(name,block,twoDMouseArray,mouseXYDir)
    def checkMouse(self, mouse):
        global twoDMouseArray
        global mouseXYDir
        currentX , currentY , direction = False,False,False
        blocks = {'initializeBlock': False, 'initialize hide': False, 'receive block': False,
                  'show block': False,'hide block': False }
        storedReceiveScripts = []
        mouseXYDir[0] = mouse.position[0]
        mouseXYDir[1] = mouse.position[1]
        mouseXYDir[2] = mouse.direction
        # check the visible scripts for the blocks
        for script in mouse.scripts:
            if not isinstance(script, kurt.Comment):
                #check for initializing hide
                if (stringContains(script.blocks[0].stringify(), ["greenFlag"])):
                    blocks["initializeBlock"] = True
                    self.doMouseInitializeBlock(script, blocks)
                    if blocks["receive block"]:
                        for storedReceiveScript in storedReceiveScripts:
                            self.doMouseReceiveBlock(storedReceiveScript, blocks)
                #check the receive block
                elif (stringContains(script.blocks[0].stringify(), ["I receive"])):
                    blocks["receive block"] = True
                    doneReceive = True
                    if (not blocks["initializeBlock"]):
                        storedReceiveScripts.append(script)
                    else:
                        self.doMouseReceiveBlock(script, blocks)
                    
        return blocks
    def checkDog(self, dog):
        global twoDDogArray
        global dogXYDir
        dogXYDir[0] = dog.position[0]
        dogXYDir[1] = dog.position[1]
        dogXYDir[2] = dog.direction
        blocks = {'initialize times hit': False,
                  'contains loop': False,
                  'loop ending condition': False,'move the dog': False,
                  'touching mouse': False, 'increment': False }
        # check the visible scripts for the blocks
        for script in dog.scripts:
            if not isinstance(script, kurt.Comment):
                #check for initializing
                if (stringContains(script.blocks[0].stringify(), ["greenFlag"])):
                    for name, _, block in self.iter_blocks(script):
                        self.arrayDoStuff(name,block,twoDDogArray,dogXYDir)
                    if scriptContains(script, [["set","0"]]):
                        blocks["initialize times hit"] = True
                    if scriptContains(script, [["forever"],["repeat"]]):
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
        global twoDDogArray
        global twoDMouseArray
        twoDDogArray = []
        twoDMouseArray = []
        for i in xrange(500):
            twoDDogArray.append([])
            twoDMouseArray.append([])
            for j in xrange(400):
                twoDDogArray[i].append(0)
                twoDMouseArray[i].append(0)
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
            mouseBlocks = {'initializeBlock': False, 'initialize hide': False, 'receive block': False,
                  'show block': False,'hide block': False }
        if dog:
            dogBlocks = self.checkDog(dog)
        else:
            dogBlocks = {'initialize times hit': False,
                  'contains loop': False,
                  'loop ending condition': False,'move the dog': False,
                  'touching mouse': False, 'increment': False }
        hitBlocks = {'dog mouse intersect' :False}
        """pointsMouse = []
        pointsDog = []
        i = 0
        while i < 500:
            j = 0
            while j < 400:
                if twoDDogArray[i][j] == 1:
                    pointsDog.append([i,j]);
                if twoDMouseArray[i][j] == 1:
                    hitBlocks['ggg'] = True
                    pointsMouse.append([i,j]);
                j += 1
            i += 1
        hitBlocks[(str)(pointsMouse)] = True
        hitBlocks[(str)(pointsDog)] = False"""
        i = 0
        while i < 500:
            j = 0
            while j < 400:
                if twoDDogArray[i][j] == 1 and twoDMouseArray[i][j] == 1:
                    hitBlocks['dog mouse intersect'] = True
                    break
                j += 1
            if hitBlocks['dog mouse intersect'] == True:
                break
            i += 1
        return {'cat': catBlocks, 'mouse': mouseBlocks, 'dog' : dogBlocks, 'test hit' : hitBlocks}
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



