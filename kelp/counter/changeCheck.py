from kelp.octopi import OctopiPlugin
import kurt
import sys
import os
from optparse import OptionParser
import projectClasses
#import classes here

#command line arguements should specify the name of the project type (all projects must be of the same type?)
#Otherwise, run all checks against all projects???? (Seems a bit much)

#hardcode (with dictionary) the number of sprites expected in a project 
#hardcode (dict) the original number of costumes
#hardcode (dict) the original scripts for the projects

#each project should have a value for number of sprites, costumes expected, along with the original scripts for each sprite 

#when run, this program should run similarly to snapshots (read in a file, or perhaps a directory?)

#try to use snapshots to read how many projects it takes to figure out distance (block repetitions + numbers) 
#import classes (must be hand-coded)
classes = {"AnimalRace":projectClasses.AnimalRace,"CAGeography":projectClasses.CAGeography,
            "CAGeographyBroadcast":projectClasses.CAGeographyBroadcast,"DanceParty":projectClasses.DanceParty,"EgyptGame":projectClasses.EgyptGame,
            "GoldRush":projectClasses.GoldRush,"IntroGame":projectClasses.IntroGame,"MammalsGame":projectClasses.MammalsGame,"Missions":projectClasses.Missions,
            "MissionsBroadcast":projectClasses.MissionsBroadcast,"Planets":projectClasses.Planets,"PlanetsBroadcast":projectClasses.PlanetsBroadcast,
            "PlantGrowing":projectClasses.PlantGrowing,"RaceGame":projectClasses.RaceGame,"ThanksgivingGame":projectClasses.ThanksgivingGame}
def main():
    parser = OptionParser(usage = "FilePath module")
    parser.add_option('-s', '--student-dir', action="store", type="string", dest="student", default=False,
                      help=('Analyze a directory of a student\'s snapshots for a project.'))
    opt, argv = parser.parse_args()
    if len(argv) == 2:
        module = argv[0]
        targetPath = argv[1]
        analyzeSingleFile(module, targetPath)
    if opt.student:
        module = argv[0]
        targetPath = opt.student
        analyzeMultipleSnaps(module, targetPath)
    
    
    

    # set up kurt project
    
def analyze(module, targetPath): #takes module arguement and path to a scratch file
    oct = kurt.Project.load(os.path.abspath(targetPath))
    l = classes[module]() #creates a class of the appropriate type based on project
    results = []
    if (len(oct.sprites)< l.spriteCount):
        results.append(str(l.spriteCount-len(oct.sprites))+" sprite(s) deleted")
    if (len(oct.sprites) == l.spriteCount):
        results.append("Correct amount of sprites")
    if (len(oct.sprites) > l.spriteCount):
        results.append(str(len(oct.sprites)-l.spriteCount)+" extra sprite(s)")
    for spriteName, spriteTuple in l.sprites.items():
        count = 0
        scriptText = spriteTuple[0]
        numCostumes = spriteTuple[1]
        for sprite in oct.sprites:
            if spriteName == sprite.name: #start checking scripts to ensure accuracy
                for script in sprite.scripts:
                    for stuff in scriptText: # for each script belonging to the sprite
                        if stuff in script.stringify(): #loop that checks for each original script
                            count += 1
                            if stuff == script.stringify():
                                results.append (spriteName + ": Script " +str(count)+" unchanged")
                            else:
                                if (l.addOkay == False):
                                    results.append (spriteName +":Script " +str(count)+" Additions Made")
                            if (len (l.sprites[spriteName][0])!=0):
                                l.sprites[spriteName][0].remove(stuff)
                if (len(sprite.costumes) < numCostumes):
                    results.append(spriteName +":Costumes Deleted")
                if (len(sprite.costumes)  == numCostumes):
                    results.append(spriteName+":Same number of costumes")
                if (len(sprite.costumes) > numCostumes):
                    results.append(spriteName +"Costumes Added")
    c = classes[module]()
    for sprite, script in l.sprites.items():
        if(len(script[0]) != 0 and (len(c.sprites[sprite][0]) != 0)):
            results.append(sprite + ":Script deletions made or script removed")
    return results    
def analyzeSingleFile(module, targetFile):
    resultsDict = {}
    resultsDict[targetFile] = analyze(module, targetFile)
    html_out(resultsDict)
def analyzeMultipleSnaps(module, targetDirectory): #runs check against all files in a directory (snapshot)
    resultsDict = {}
    for scratchFile in os.listdir(targetDirectory):
        resultsDict[scratchFile] = analyze(module, targetDirectory+'\\'+scratchFile)
    html_out(resultsDict)
def html_out(resultsDict):
    if not os.path.exists('results'):
        os.mkdir('results')
    html = []
    if not os.path.exists('results/output.html'):
        for project, list in resultsDict.items():
            html.append("<h2>" + project + "</h2>")
            for item in list:
                html.append("<p>"+item +"<p>")
        with open('results/output.html', 'w') as fp:
            fp.write(''.join(html))
    #write out all results to a single page. 


if __name__ == "__main__":
    main()