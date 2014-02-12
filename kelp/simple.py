from kelp.octopi import OctopiPlugin
from kelpplugin import KelpPlugin
import kurt

class SimpleMaze(KelpPlugin):
	def __init__(self): 
		super(SimpleMaze, self).__init__()
	def analyze(self, scratch):
		p = kurt.Project.load("simple.oct")
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
			for costume in scriptable.costumes:
				count = count +1 
			if count > 2 :
				dict.append( '<h2 style = "background-color:yellow"> Please delete all extra costumes</h2>')
			if count == 2:
				dict.append( '<h2 style = "background-color:yellow"> Perfect!</h2>')
			if count < 2: 
				dict.append( '<h2 style = "background-color:yellow"> You need at least two costumes to do this :)')
			for script in scriptable.scripts: 
				for string in arrows: #Checks to see if all arrow keys have a block
					if string in script.blocks[0].stringify(): #checks to see if any of the arrow keys are this block. 
						completed.append(script) #completed is a stupid name. Change it. 
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
				dict.append('<h2 style = "background-color:Pink" size = "12" ')
				for string in arrows2:
					dict.append(' <p>Close! Check the  ' + string + ' block. It may still need to move or switch costumes</p>') 
				dict.append('</h2>')
			
			if (len(directionIncorrect) > 0 ): 
				dict.append('<h2 style = "background-color:Blue" size = "12" >')
				for item in directionIncorrect:
					for string in arrows3:
						if (string in item.blocks[0].stringify()):
							dict.append('<p> Whoops! It looks like the ' + string + ' arrow makes the Hero move in the wrong direction!</p>')
				dict.append('<\h2>')
		return dict
		
def maze_display(mydictionary):
	
	return ''.join(mydictionary)
			

			