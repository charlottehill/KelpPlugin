"""This plugin is for the Predator Prey Project &  Sequence Lesson."""

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
                seq[var] = scratch.variables[var]
            else:
                seq[var] = '-1'
        return seq

def predator_display(seq):
    html = []
    # variables                                                                                                  
    backgroundColor = 'LightSkyBlue'

    #if student completes level 0
    if seq['Level'].value >= 1:
        # if student makes 0 mistakes
        if seq['Level 0 Incorrect Pick-ups'].value == 0:
            backgroundColor = 'lime'
            html.append('<h2 style="background-color:{1};"> This student completed Level 0 with no incorrect animal pickups</h2>'.format(seq['Level 0 Incorrect Pick-ups'].value, backgroundColor))
        else:
            html.append('<h2 style="background-color:{1};"> This student completed Level 0 with {0} incorrect animal pickups out of 1 possible incorrect animal pickups</h2>'.format(seq['Level 0 Incorrect Pick-ups'].value, backgroundColor))
    #student did NOT complete Level 0
    else:
        html.append('<h2 style="background-color:{0};"> This student did not complete Level 0 </h2>'.format(backgroundColor))

    html.append('<br>')

    backgroundColor = 'LightSkyBlue'
    #if student completes Level 1
    if seq['Level'].value >= 2:
        #if student does Level 1 w/ 0 mistakes
        if seq['Level 1 Incorrect Pick-ups'].value == 0:
            backgroundColor = 'lime'
            html.append('<h2 style="background-color:{1}"> This student completed Level 1 with no incorrect animal pickups</h2>'.format(seq['Level 1 Incorrect Pick-ups'].value, backgroundColor))
        else:
            html.append('<h2 style="background-color:{1}"> This student completed Level 1 with {0} incorrect pickups out of 2 possible incorrect animal pickups</h2>'.format(seq['Level 1 Incorrect Pick-ups'].value, backgroundColor))
    else:
        html.append('<h2 style="background-color:{0}"> This student did not complete Level 1 </h2>'.format(backgroundColor))
    
    return ''.join(html)
