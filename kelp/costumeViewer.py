"""This plugin is for Lesson 4: Costume Changes."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
from broadcastViewer import Broadcast
from initializationViewer import Initialization
import os
import sys
import kurt

'''How to run this plugin:
	hairball -k <path>/octopi.py -d <folder where sequenceViewer is> -p sequenceViewer.Sequence test.sb
	For example, if `octopi.py` and sequenceViewer are both in the directory where you are:
    hairball -k octopi.py -d . -p sequenceViewer.Sequence test.sb
    if sequenceViewer is in your directory but octopi.py is right outside of it:
    hairball -k ../octopi.py -d . -p sequenceViewer.Sequence test.sb
    If they're both right outside of it:
    hairball -k ../octopi.py -d .. -p sequenceViewer.Sequence test.sb
'''

class Costumes(KelpPlugin):

    def __init__(self):
        super(Costumes, self).__init__

    def analyze(self, scratch, **kwargs):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)
        projectName = scratch.name
        self.costumes = dict()
        self.costumes['Stage'] = set()
        index = 0
        for background in scratch.stage.backgrounds:
            self.costumes['Stage'].add(self.save_png(projectName, background, index, 'Stage'))
            index += 1
        for sprite in scratch.sprites:
            index = 0
            self.costumes[sprite.name] = set()
            for costume in sprite.costumes:
                self.costumes[sprite.name].add(self.save_png(projectName, costume, index, sprite.name))
                index += 1
        return self.costumes


def costume_display(costumes):
    html = []
    html.append('\n<p>COSTUMES</p>')
    html.append('\n<table>')
    html.append('\n  <tr>')
    for sprite in costumes.keys():
        html.append('\n    <th>{0}</th>'.format(sprite))
    html.append('\n  </tr>')
    html.append('\n  <tr>')
    for sprite, values in costumes.items():
        html.append('\n<td>')
        for value in values:
            html.append('\n    <p><img src="{0}" height="100" width="100"></p>'.format(value))
        html.append('\n</td>')
    html.append('\n  </tr>')
    html.append('\n</table>')
    return ''.join(html)
