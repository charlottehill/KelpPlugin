#!/usr/bin/env python

from __future__ import print_function
from collections import Counter
from eventViewer import *
from broadcastViewer import *
from sequenceViewer import *
from initializationViewer import *
from costumeViewer import *
from kelpplugin import KelpPlugin
from octopiplugin import OctopiPlugin
import os
import sys
import kurt
from octopiplugin import OctopiPlugin
from hairball import Hairball


#to run: python offline.py file_name.oct plugin_directory lesson_name project_concept(optional)

lessons = {'sequential': frozenset(['predatorprey', 'egypt', 'thanksgiving']),
           'events': frozenset(['planets', 'racing', 'musical', 'piano']),
           'initialization': frozenset(['game']),
           'broadcast': frozenset(['ca', 'missions', 'instruments']),
           'costumes': frozenset(['racing']),
           'scenes': frozenset(['goldrush'])}

plugins = {'sequential': frozenset(['sequenceViewer.Sequence', 'sequenceViewer.Screenshot']),
           'events': frozenset(['eventViewer.Events', 'sequenceViewer.Screenshot']),
           'initialization': frozenset(['initializationViewer.Initialization', 'eventViewer.Events']),
           'broadcast':frozenset(['broadcastViewer.Broadcast', 'eventViewer.Events']),
           'costumes': frozenset(['costumeViewer.Costumes', 'broadcastViewer.Broadcast',
                                  'initializationViewer.Initialization', ]),
           'scenes': frozenset(['costumeViewer.Costumes'])}

htmlwrappers = {'Sequence': sequence_display,
                'Screenshot': project_screenshot,
                'Initialization': initialization_display,
                'Events': event_display,
                'Broadcast': broadcast_display,
                'Costumes': costume_display}


def html_view(title):
    html = []
    html.append('\n<html>')
    html.append('\n<head>')
    html.append('\n<meta charset="utf8">')
    html.append('\n<title>{0}</title>'.format(title))
    
    #<!-- Include jQuery -->
    html.append('\n<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>')

    #<!-- Include scratchblocks2 files -->
    html.append('\n<link rel="stylesheet" href="//charlottehill.com/scratchblocks/build/scratchblocks2.css">')
    html.append('\n<link rel="stylesheet" type="text/css" href="style.css">')
    html.append('\n<script src="//charlottehill.com/scratchblocks/build/scratchblocks2.js"></script>')
    
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
    # go through the command line arguments
    path = sys.argv[1]
    directory = sys.argv[2]
    lesson = sys.argv[3]
    if (len(sys.argv) > 4):
        project = sys.argv[5]
    else:
        project = 'default'

    # set up kurt project
    kurt.plugin.Kurt.register(OctopiPlugin())
    oct = kurt.Project.load(path)
    oct.hairball_prepared = False

    
    # make lists of all the plugins and views
    plugin_list = ['hairball', '-k', 'octopiplugin.py', '-d', directory]
    view_list = []
    if lesson not in plugins.keys():
        exit(1)
    for proj in plugins[lesson]:
        plugin_list.append('-p')
        plugin_list.append(proj)
    if (project != 'default'):
        if project in plugins.keys():
            for extra in plugins[project]:
                plugin_list.append('-p')
                plugin_list.append(extra)
    plugin_list.append(path)

    # initialize Hairball and html
    hairball = Hairball(plugin_list)
    hairball.initialize_plugins()
    html_list = [html_view(lesson)]

    # for each plugin, run Hairball and the associated view
    for plugin in hairball.plugins:
        name = plugin.__class__.__name__
        results = plugin._process(oct)
        html_list.append(htmlwrappers[name](results))
    
    # add on the closing html (to do)
    html_list.append('</body>')
    html_list.append('</html>')

    # write to the file (to do: change file and directory names)
    file = open('results/{0}_{1}.html'.format(lesson, project), 'w')
    file.write(''.join(html_list))
    file.close()

main()
