from kelp.octopi import OctopiPlugin
from kelpplugin import KelpPlugin
from . import simple
import kurt


class ComplexMaze(KelpPlugin):
    def __init__(self):
        super(ComplexMaze, self).__init__()

    def analyze (self, scratch):
        lister = []
        winningScript = []
        hitScript = []
        switch = 0
        switch2 = 0
        output = []
        SendWin = False
        SendHit = False
        moveStart = False
        WinScriptSet = False
        BLOCKMAPPING = {
'costume': frozenset([('switch backdrop to', 'absolute'),
                      ('next backdrop', 'relative'),
                      ('switch costume to', 'absolute'),
                      ('next costume', 'relative')]),

'position': frozenset([('move', 'relative'),
                       ('glide', 'relative'),
                       ('go to', 'absolute'),
                       ('change x by', 'relative'),
                       ('x position', 'absolute'),
                       ('change y by', 'relative'),
                       ('y position', 'absolute')])
                       }

        for sprite in scratch.sprites: #checks to see if the key detects a hit rather than the hero doing so
            if "ey" in sprite.name:
                if len(sprite.scripts) != 0:
                    for script in sprite.scripts:
                        for block in script:
                            if "win" in block.stringify() and "broadcast" in block.stringify():
                                SendWin = True

        for sprite in scratch.sprites: #this code block gets hero sprite
            if "Hero" in sprite.name:
                for script in sprite.scripts:
                    if not isinstance(script, kurt.Comment): #sorts out comments
                        for block in script.blocks:
                            if "Flag" in block.stringify():  #puts Green Flag scripts into a list
                                lister.append(script)

        for script in lister: #check the green flag scripts
            for block in script.blocks:
                for string in BLOCKMAPPING['position']:
                    if string[0] in block.stringify() and "forever" not in block.stringify():
                        moveStart = True
                if "forever" in block.stringify() and "broadcast" in block.stringify():
                    if ("hit") in block.stringify():
                        SendHit = True
                    if ("win") in block.stringify():
                        SendWin = True

        #for the stage
        for script in scratch.stage.scripts: #check to see if the messages are being received
            for block in script.blocks:
                if "win" in block.args:
                    output.append("<h2 style = background-color:Green> Receiving win block set!</h2>") # or set WON BLOCK to true
                    winningScript.append(script)

                if "hit" in block.stringify():
                    output.append("<h2 style = background-color:Green> Receiving hit block set! </h2>") # or set HIT BLOCK to true
                    hitScript.append(script)

        if (len(winningScript) == 0):
            output.append('<h2 style = "background-color:Pink"> There\'s no script for what happens when "Win" is sent </h2>')
        else:
            for block in winningScript[0].blocks: #checks to see if the background somehow switches on victory
                if "background1" in block.args:
                    WinScriptSet = True
        if (len(hitScript) == 0):
            output.append('<h2 style = "background-color:Pink"> There\'s no script for what happens when "Hit" is sent </h2>')
        else:
            for block in hitScript[0].blocks:
                if "maze1" in block.args:
                    switch += 1
                if "maze" in block.args and "maze1" not in block.args:
                    switch2 += 1
        if switch >= 1 and switch2 >= 1 and switch2 == switch: # there is at least one block for each background
            output.append("<h2 style = 'background-color:Green'>Your maze is correctly switching colors!</h2>")
        if switch < 1 or switch2 < 1 or switch2 != switch: # one or more of the backgrounds does not have a block
            output.append("<h2 style = 'background-color:Yellow'> Your maze doesn't switch colors or doesn't switch back to the original color </h2>")

        checkStart = []
        bswitch = 0
        for script in scratch.stage.scripts:
            for block in script.blocks:
                if ("Flag") in block.stringify():
                    checkStart.append(script)
        if (len(checkStart) == 0):
            output.append("<h2 style = background-color:Pink>You need some way to switch the maze back to the starting background at the beginning. Try using a Green Flag!</h2>")
        else:
            for block in checkStart[0].blocks:
                if "switch" in block.stringify():
                    bswitch = 1;
        if (bswitch == 1):
            output.append("<h2 style = background-color:Green> Good work! The maze correctly switches backgrounds at the beginning</h2>")
        else:
            output.append("<h2 style=  background-color:Yellow> Close! You still need a block to make the maze switch to the correct background after the Flag is pressed</h2>")

        if (SendWin == True):
            output.append("<h2 style = background-color:Green> 'Win' is successfully broadcast </h2>")
        else:
            output.append("<h2 style = background-color:Pink> 'Win' isn't being broadcast </h2>")
        if (SendHit == True):
            output.append("<h2 style = background-color:Green> 'Hit' is successfully broadcast </h2>")
        else:
            output.append("<h2 style = background-color:Pink> 'Hit' isn't being broadcast </h2>")
        if (moveStart == True):
            output.append("<h2 style = background-color:Green> Good! Now the Hero knows where to go at the start!</h2>") #means the hero has a start position that resets
        else:
            output.append("<h2 style = background-color:Pink> Uh-oh! The hero doesn't know how to get back to the start </h2>")
        if (WinScriptSet == True):
            output.append("<h2 style = 'background-color:Green'> You successfully implemented the winning script<h2>")
        else:
            output.append("<h2 style = background-color:Yellow> The wining background isn't displayed when 'Win' is sent </h2>")
        #################################### Arrow Keys Below
        arrowChecker = simple.SimpleMaze()
        dict = simple.SimpleMaze.analyze(arrowChecker, scratch)
        return output + dict
def complex_MazeDisplay(myDictionary):
    return ''.join(myDictionary)
