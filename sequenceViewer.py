"""This plugin is for Lesson 1: Sequence."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
import os
import sys
import kurt
import PIL

'''How to run this plugin:
	hairball -k <path>/octopi.py -d <folder where sequenceViewer is> -p sequenceViewer.Sequence test.sb
	For example, if `octopi.py` and sequenceViewer are both in the directory where you are:
    hairball -k octopi.py -d . -p sequenceViewer.Sequence test.sb
    if sequenceViewer is in your directory but octopi.py is right outside of it:
    hairball -k ../octopi.py -d . -p sequenceViewer.Sequence test.sb
    If they're both right outside of it:
    hairball -k ../octopi.py -d .. -p sequenceViewer.Sequence test.sb
'''


class Sequence(KelpPlugin):
    def __init__(self):
        super(Sequence, self).__init__

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        seq = dict()
        # store the screen
        seq['screen'] = KelpPlugin.save_png(scratch.name, scratch.thumbnail, 'screen');

        #store the values for the variables level and points, if they exist
        level = False
        points = False

        for name, var in scratch.variables.items():
            if name == 'level' or name == 'Level':
                level = True
                seq[name] = var.value
            elif name == 'points' or name == 'Points':
                points = True
                seq[name] = var.value

        # If they don't exist, store them with the value of -1
        if level == False:
            seq['level'] = '-1'
        if points == False:
            seq['points'] = '-1'

    	return seq

class Screenshot(KelpPlugin):
    def __init__(self):
        super(Screenshot, self).__init__

    def analyze(self, scratch):
        self.thumbnails = dict()
        self.thumbnails['screen'] = KelpPlugin.save_png(scratch.name, scratch.thumbnail, 'screen')
        return self.thumbnails

def project_screenshot(thumbnails):
    html = []
    html.append('\n    <h2> Screenshot of Octopi Project </h2>')
    html.append('\n    <td><img src="{0}"'.format(thumbnails['screen']))
    html.append('height="240" width="320" border="1"></td>')
    return ''.join(html)

def sequence_display(seq):
    html = []
    # variables
    for var in ['level', 'points']:
        if seq[var] == '-1': #if they don't exist don't print them out
            html.append('<p>The variable <b>' + var + ' </b>does not exist</p>')
        else:
            html.append('<p>{0}: {1}</p>'.format(var, seq[var]))
    return ''.join(html)
