"""This plugin is for Lesson 2: Events."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
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

BASE_PATH = './results'


class Events(KelpPlugin):

    def __init__(self):
        super(Events, self).__init__()

        """Returns a dictionary of the scripts.
        Keys: start events
        Values: another dictionary
        Keys: sprite names
        Values: that sprite's scripts for this start event ."""

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)
        #initialize
        self.types = dict()
        self.types[self.NO_HAT] = dict()
        self.types[self.HAT_GREEN_FLAG] = dict()
        self.types[self.HAT_WHEN_I_RECEIVE] = dict()
        self.types[self.HAT_KEY] = dict()
        self.types[self.HAT_MOUSE] = dict()
        for event in self.types.keys():
            for morph in scratch.sprites + [scratch.stage]:
                self.types[event][morph.name] = {"hidden": set(), "visible": set()}

        #go through the visible scripts
        for sprite, script in KelpPlugin.iter_sprite_visible_scripts(scratch):
            if not script.reachable:
                self.types[self.NO_HAT][sprite]["visible"].add(script)
            elif KelpPlugin.script_start_type(script) in self.types.keys():
                self.types[KelpPlugin.script_start_type(script)][sprite]["visible"].add(script)
        #go through the hidden scripts
        for sprite, script in KelpPlugin.iter_sprite_hidden_scripts(scratch):
            if not script.reachable:
                self.types[self.NO_HAT][sprite]["hidden"].add(script)
            elif KelpPlugin.script_start_type(script) in self.types.keys():
                self.types[KelpPlugin.script_start_type(script)][sprite]["hidden"].add(script)
        return {'events': self.types, 'thumbnails': self.thumbnails(scratch)}


def event_display(results):
	thumbnails = results['thumbnails']
	events = results['events']
        # Displays sprite names and pictures
        html = []
        html.append('<table border="1"><tr><th class=noBorder></th>')
        sprites = []
        for sprite in thumbnails.keys():
            if sprite != 'screen':
                sprites.append(sprite)
                html.append('    <th>{0}</th>'.format(sprite))
        html.append('</tr>  <tr><td class="noBorder" ></td>')
        for sprite in sprites:
            html.append('    <td><img src="{0}" height="100" width="100" style="float:center"></td>'.format(thumbnails[sprite]))
        html.append('</tr>')

        # Displays scripts
        for event_type, event in events.items():
            html.append('<tr><td class = "noBorder"><b>{0}</b></td>'.format(KelpPlugin.SCRIPT_TITLES[event_type]))
            for sprite in sprites:
            	html.append('  <td>')
            	visible = ""
            	hidden = ""
                if event[sprite]['hidden']:
                    for script in event[sprite]['hidden']:
                    	hidden += KelpPlugin.to_scratch_blocks(sprite, script)
                	html.append('<pre class="hidden"><p>{0}</p></pre>'.format(hidden))
            	if event[sprite]['visible']:
                    for script in event[sprite]['visible']:
                    	visible += KelpPlugin.to_scratch_blocks(sprite, script)
                	html.append('<pre class="blocks"><p>{0}</p></pre>'.format(visible))
            	html.append('  </td>')
            html.append('  </tr>')
        return ''.join(html)

