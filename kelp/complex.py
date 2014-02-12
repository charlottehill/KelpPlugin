from kelp.octopi import OctopiPlugin
from kelpplugin import KelpPlugin
import kurt

class ComplexMaze(KelpPlugin):
	def  __init__(self):
		super(ComplexMaze, self).__init__()
	def analyze (self, scratch): 
		p = kurt.Project.load("complex.oct")
		lister = []
		second = []
		stage = []
		completed = []
		winningScript = []
		hitScript = []
		hero = []
		switch = 0 
		switch2 = 0
		output = []
		for sprite in p.sprites: #this code block gets hero sprite
			if "Hero" in sprite.name:
				hero.append(sprite) 
				
		for script in hero[0].scripts:  #iterates through all scripts in the Hero class
			if not isinstance(script, kurt.Comment): #sort out comments
				for block in script.blocks:
					if "Flag" in block.stringify(): #puts all Green Flag scripts into list
						lister.append(script)
						
		for script in lister: #check the green flag scripts
			for block in script.blocks:
				if "go to" in block.stringify() and "forever if" not in block.stringify(): 
					output.append("<h2 style = background-color:Green> Good! Now the Hero knows where to go at the start!</h2>") #means the hero has a start position that resets
				if "forever if" in block.stringify() and "touching" in block.stringify():
						completed.append(block) #second.append(block)
						
		if len(completed) == 2:
			output.append("<h2 style = 'background-color:Green'> All forever loops completed successfully </h2>")
		elif len(completed) < 2:
			output.append("<h2 style = 'background-color:Yellow'> You still need to implement some forever-if loops</h2>")

		#for the stage
		for script in p.stage.scripts: #check to see if the messages are being received 
			for block in script.blocks: 
				if "win" in block.args:
					output.append("<h2 style = background-color:Green> Win block Set!</h2>") # or set WON BLOCK to true
					winningScript.append(script)
						
				if "hit" in block.stringify():
					output.append("<h2 style = background-color:Green> Hit Block Set! </h2>") # or set HIT BLOCK to true
					hitScript.append(script)
		
		if (len(winningScript) == 0):
			output.append('<h2 style = "background-color:Pink"> There\'s no script for what happens when "Win" is sent </h2>') 
		else:
			for block in winningScript[0].blocks: #checks to see if the background somehow switches on victory
				if "background1" in block.args: 
					output.append("<h2 style = 'background-color:Green'> You successfully implemented the winning script<h2>") 
		if (len(hitScript) == 0):
			output.append('<h2 style = "background-color:Pink"> There\'s no script for what happens when "Hit" is sent </h2>')
		else:
			for block in hitScript[0].blocks:
				if "maze1" in block.args:
					switch += 1
				if "maze" in block.args:
					switch2 += 1
		if switch > 1 and switch2 >= 1: 
			output.append("<h2 style = 'background-color:Green'>Your maze is correctly switching!</h2>") #or set maze-switching to true 
		if switch < 1 or switch2 < 1:
			output.append("<h2 style = 'background-color:Yellow'> Your maze doesn't switch colors</h2>") #set maze-switching to false
		
		checkStart = []
		bswitch = 0
		for script in p.stage.scripts:
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
			#################################### Arrow Keys Below
		count = 0
		arrows = ["left", "right", "up", "down"]
		arrows2 = list(arrows)
		arrows3 = list(arrows)
		completed = []
		dict = []
		hasMotion = []
		hasCostume = []
		directionCorrect = []
		directionIncorrect = []
		Hero = []
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
		for sprite in p.sprites:
			if "ero" in sprite.name:
				Hero.append(sprite)
		for scriptable in Hero:
			if not isinstance(scriptable, kurt.Comment):
				for costume in scriptable.costumes:
					count = count +1 
				if count > 2 :
					dict.append( '<h2 style = "background-color:yellow"> Please delete all extra costumes</h2>')
				if count == 2:
					dict.append( '<h2 style = "background-color:yellow"> Perfect!</h2>')
				if count < 2: 
					dict.append( '<h2 style = "background-color:yellow"> You need at least two costumes </h2>')
				for script in scriptable.scripts: 
					if not isinstance(script, kurt.Comment):
						for string in arrows: #Checks to see if all arrow keys have a block
							if string in script.blocks[0].stringify(): #checks to see if any of the arrow keys are this block. 
								completed.append(script) #Add the script to a list
								arrows.remove(string)#if so, then remove the arrow key from the list of possibilities
							
				for script in completed: 
					for block in script.blocks: 
						for tuple in BLOCKMAPPING['position']:
							if tuple[0] in block.stringify():
								hasMotion.append((script, block)) 
				#check direction of motion to ensure that it is + -  as needs be 
				
				for tuple in hasMotion: #checks to see if motion is in the correct direction 
					if 'left arrow key'in tuple[0].blocks[0].stringify() or 'down arrow key' in tuple[0].blocks[0].stringify():
						if tuple[1].args[0]/-1 == abs(tuple[1].args[0]):
							directionCorrect.append(tuple[0])
						else:
							directionIncorrect.append(tuple[0])
					if 'right arrow key' in tuple[0].blocks[0].stringify() or 'up arrow key' in tuple[0].blocks[0].stringify(): 
						if tuple[1].args[0] == abs(tuple[1].args[0]):
							directionCorrect.append(tuple[0])
						else:
							directionIncorrect.append(tuple[0])
				
				for script in directionCorrect:
					for block in script.blocks:
						for tuple in BLOCKMAPPING['costume']: 
							if tuple[0] in block.stringify(): 
								hasCostume.append(script.blocks[0].stringify()) # if at this point, it is completely correct - direction
						
				if (len(arrows) != 0): 
					dict.append(' <h2 style = "background-color:Blue">  ')
					for string in arrows:
						dict.append( '<p>There is no block for the '  + string + ' arrow</p>')
					dict.append('</h2>')
				else: 
					dict.append('<h2 style = "background-color:Blue"> Good! All arrows implemented</h2>')
				for item in hasCostume: 
					for string in arrows2:
						if (string in item):
							arrows2.remove(string)
							
				if(len(arrows2) > 0 ):
					dict.append('<h2 style = "background-color:Pink" ')
					for string in arrows2:
						dict.append(' <p>Close! Check the  ' + string + ' block. It may still need to move or switch costumes</p>') 
					dict.append('</h2>')
				
				if (len(directionIncorrect) > 0 ): 
					dict.append('<h2 style = "background-color:Blue" >')
					for item in directionIncorrect:
						for string in arrows3:
							if (string in item.blocks[0].stringify()):
								dict.append('<p> Whoops! It looks like the ' + string + ' arrow makes the Hero move in the wrong direction!</p>')
					dict.append('</h2>')
				
				
			return output + dict
def complex_MazeDisplay(myDictionary):
	return ''.join(myDictionary)


		
		