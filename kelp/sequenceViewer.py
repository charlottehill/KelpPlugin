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

        #store the values for the variables level, points, and health if they exist

        name = ['Level', 'Points', 'Health']
        for var in name:
            if var in scratch.variables.keys():
                seq[var] = scratch.variables[var]
            else:
                seq[var] = '-1'
        return seq

class Screenshot(KelpPlugin):
    def __init__(self):
        super(Screenshot, self).__init__

    def analyze(self, scratch):
        self.thumbnails = dict()
        self.thumbnails['screen'] = self.save_png(scratch.name, scratch.thumbnail, 'screen')
        return self.thumbnails

def project_screenshot(thumbnails):
    html = []
    html.append('\n    <h2>Screenshot of Octopi Project </h2>')
    ##below used to add the screen shot to the table if there was one, we want it to be separate
    #html.append('\n    <td><img src="{0}"'.format(thumbnails['screen']))
    #html.append('height="240" width="320" border="1"></td>')
    html.append('\n    <img src="{0}"'.format(thumbnails['screen']))
    html.append('height="240" width="320" style="border:5px solid black">')
    return ''.join(html)

def sequence_display(seq):
    html = []
    # variables
    for var in seq.keys():
        if seq[var] == '-1': #if they don't exist don't print them out
            html.append('<h3>The variable <b>' + var + ' </b>does not exist</h3>')
        else:
            html.append('<h3>{0} has a value of {1}</h3>'.format(var, seq[var].value))
    return ''.join(html)
