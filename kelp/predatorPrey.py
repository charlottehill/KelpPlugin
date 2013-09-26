"""This plugin is for the Predator Prey Project &  Sequence Lesson."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
import os
import sys
import kurt
import PIL
import pprint

'''How to run this plugin:
        hairball -k <path>/octopi.py -d <folder where sequenceViewer is> -p sequenceViewer.Sequence test.sb
        For example, if `octopi.py` and sequenceViewer are both in the directory where you are:
    hairball -k octopi.py -d . -p sequenceViewer.Sequence test.sb
    if sequenceViewer is in your directory but octopi.py is right outside of it:
    hairball -k ../octopi.py -d . -p sequenceViewer.Sequence test.sb
    If they're both right outside of it:
    hairball -k ../octopi.py -d .. -p sequenceViewer.Sequence test.sb
'''


class Predator(KelpPlugin):
    def __init__(self):
        super(Predator, self).__init__

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        seq = dict()

        #store the values for the variables level, points, and health if they exist

        name = ['Level', 'Points', 'Health', 'Level 0 Incorrect Pick-ups', 'Level 1 Incorrect Pick-ups']

        for var in name:
            if var in scratch.variables.keys():
                #print(scratch.variables[var])
                seq[var] = int(scratch.variables[var].value)
            else:
                seq[var] = -1
        return seq

def predator_display(seq):
    html = []

    backgroundColor = 'LightBlue'

    #pprint.pprint(seq)

    if seq['Level'] >= 1:
        if seq['Level 0 Incorrect Pick-ups'] == 0: #perfect level
            backgroundColor = 'LightGreen'
            html.append('<h2 style="background-color:{0}">'.format(backgroundColor))
            html.append('Congratulations! Level 0 was completed with no incorrect animal pickups.')
            html.append('</h2>')
        else:
            html.append('<h2 style="background-color:{0}">'.format(backgroundColor))
            html.append('Level 0 was completed with ')
            html.append('{0} incorrect animal pick-ups.'.format(seq['Level 0 Incorrect Pick-ups']))
            html.append('</h2>')
    else:
            html.append('<h2 style="background-color:{0}">'.format(backgroundColor))
            html.append('Level 0 was not completed.')
            html.append('<h2>')

    html.append('<br>')

    backgroundColor = 'LightBlue'

#if student completes Level 1
    if seq['Level'] >= 2:
        #if student does Level 1 w/ 0 mistakes
        if seq['Level 1 Incorrect Pick-ups'] == 0:
            backgroundColor = 'LightGreen'
            html.append('<h2 style="background-color:{0}"> Congratulations! Level 1 was completed with no incorrect animal pickups.</h2>'.format(backgroundColor))
        else:
            html.append('<h2 style="background-color:{0}">Level 1 was completed with {1} incorrect pickups out of 2 possible incorrect animal pickups.</h2>'.format(backgroundColor,seq['Level 1 Incorrect Pick-ups'].value))
    else:
        html.append('<h2 style="background-color:{0}"> Level 1 was not completed.</h2>'.format(backgroundColor))

    return ''.join(html)
