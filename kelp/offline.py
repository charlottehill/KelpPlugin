#!/usr/bin/env python
from __future__ import print_function
from . import broadcastViewer
from . import costumeViewer
from . import eventViewer
from . import initializationViewer
from . import sequenceViewer
from . import danceParty
from . import planets
from . import planetspart1
from . import planetspart2
from . import predatorPrey
from . import raceInitialization
from . import geographyBroadcast
from . import goldRush
from . import bonus
from . import plants
from octopi import OctopiPlugin  # noqa
from optparse import OptionParser
import kurt
import sys


# to run: kelp name.oct lesson_name [project_concept]

lessons = {'sequential': frozenset(['predatorprey', 'egypt', 'thanksgiving']),
           'events': frozenset(['planets', 'racing', 'musical', 'piano']),
           'initialization': frozenset(['game']),
           'broadcast': frozenset(['ca', 'missions', 'instruments']),
           'costumes': frozenset(['racing', 'dance']),
           'scenes': frozenset(['goldrush'])}

plugins = {'sequential': [ sequenceViewer.Screenshot],
           'events': [eventViewer.Events, sequenceViewer.Screenshot],
           'initialization': [initializationViewer.Initialization,
                              eventViewer.Events],
           'broadcast': [broadcastViewer.Broadcast, eventViewer.Events],
           'costumes': [costumeViewer.Costumes, broadcastViewer.Broadcast,
                        initializationViewer.Initialization],
           'scenes': [costumeViewer.Costumes],
           'predator': [predatorPrey.Predator],
           'dance': [danceParty.DancePartyProject],
           'planets': [planets.PlanetsProject],
           'part1': [planetspart1.PlanetsProjectPart1],
           'part2': [planetspart2.PlanetsProjectPart2],
           'racing': [raceInitialization.raceInitialization],
           'cageobcast': [geographyBroadcast.geographyBroadcast],
           'gold': [goldRush.GoldRush],
           'plants': [plants.Plants],
           'bonus': [bonus.Bonus]}


# 'ClassName': filename.displayfunction
htmlwrappers = {'Sequence': sequenceViewer.sequence_display,
                'Screenshot': sequenceViewer.project_screenshot,
                'Initialization': initializationViewer.initialization_display,
                'Events': eventViewer.event_display,
                'Broadcast': broadcastViewer.broadcast_display,
                'Costumes': costumeViewer.costume_display,
                'Predator': predatorPrey.predator_display,
                'raceInitialization': raceInitialization.initialization_display,
                'DancePartyProject': danceParty.danceProj_display,
                'PlanetsProject': planets.planetProj_display,
                'PlanetsProjectPart1': planetspart1.planetProj_display,
                'PlanetsProjectPart2': planetspart2.planetProj_display,
                'geographyBroadcast': geographyBroadcast.geography_display,
                'GoldRush': goldRush.goldRush_display,
                'Plants': plants.plant_display,
                'Bonus': bonus.bonus_display}

def html_view(title):
    html = []
    html.append('\n<html>')
    html.append('\n<head>')
    html.append('\n<meta charset="utf8">')
    #title() makes first letter capital
    html.append('\n<h1 style="text-align:center">{0} Lesson</h1>'.format(title.title()))
    html.append('<hr>')
    #<!-- Include jQuery -->
    html.append('\n<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/'
                'jquery.min.js"></script>')

    #<!-- Include scratchblocks2 files -->
    html.append('\n<link rel="stylesheet" href="//charlottehill.com/'
                'scratchblocks/build/scratchblocks2.css">')
    html.append('\n<link rel="stylesheet" type="text/css" href="style.css">')
    html.append('\n<script src="//charlottehill.com/scratchblocks/build/'
                'scratchblocks2.js"></script>')

    #<!-- Parse blocks -->
    html.append('\n<script>')
    html.append('\n$(document).ready(function() {')
    html.append('\n     scratchblocks2.parse("pre.blocks");')
    html.append('\n     scratchblocks2.parse("pre.hidden");')
    html.append('\n     scratchblocks2.parse("pre.error");')
    html.append('\n     });')
    html.append('\n</script>')
    html.append('\n</script>')
    html.append('\n</head>')
    return ''.join(html)


def main():
    parser = OptionParser(usage='%prog FILENAME.oct LESSON [PROJECT]')
    options, args = parser.parse_args()
    if len(args) < 2 or len(args) > 3:
        parser.error('Incorrect number of arguments.')
    # go through the command line arguments
    path = args[0]
    lesson = args[1]
    project = args[2] if len(args) > 2 else None

    # Verify the lesson
    if lesson not in plugins:
        print('Lession `{}` not valid. Goodbye!'.format(lesson))
        sys.exit(1)
    # Add the project-specific plugins
    if project != None:
        x = plugins[project][0]
        plugins[lesson].insert(0,x)
    #plugins[lesson].extend(lessons.get(project, []))

    # set up kurt project
    octo = kurt.Project.load(path)
    octo.hairball_prepared = False


    # Prepare the output result
    html_list = [html_view(lesson)]

    # Call the plugins directly (hairball isn't really needed)
    for plugin_class in plugins[lesson]:
        plugin = plugin_class()
        name = plugin.__class__.__name__
        results = plugin._process(octo)
        html_list.append(htmlwrappers[name](results))



    # add on the closing html (to do)
    html_list.append('</body>')
    html_list.append('</html>')

    # write to the file (to do: change file and directory names)
    with open('{0}_{1}.html'.format(lesson,project), 'w') as fp:
        fp.write(''.join(html_list))

if __name__ == '__main__':
    sys.exit(main())
