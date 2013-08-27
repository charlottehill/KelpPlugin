"""This plugin is for Lesson 2: Events."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
import os
import sys
import kurt

'''How to run this plugin:
	hairball -k <path>/octopiplugin.py -d <folder where sequenceViewer is> -p sequenceViewer.Sequence test.sb
	For example, if octopiplugin and sequenceViewer are both in the directory where you are:
    hairball -k octopiplugin.py -d . -p sequenceViewer.Sequence test.sb
    if sequenceViewer is in your directory but octopiplugin.py is right outside of it:
    hairball -k ../octopiplugin.py -d . -p sequenceViewer.Sequence test.sb
    If they're both right outside of it:
    hairball -k ../octopiplugin.py -d .. -p sequenceViewer.Sequence test.sb
'''

BASE_PATH = './results'


class Events(KelpPlugin):

    def __init__(self):
        super(Events, self).__init__


    def ScriptsType(self, scratch):
        """Returns a dictionary of the scripts.
        Keys: start events
        Values: another dictionary
        Keys: sprite names
        Values: that sprite's scripts for this start event ."""

        #initialize
        self.types = dict()
        self.types["dead"] = dict()
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
                self.types["dead"][sprite]["visible"].add(script)
            elif KelpPlugin.script_start_type(script) in self.types.keys():
                self.types[KelpPlugin.script_start_type(script)][sprite]["visible"].add(script)
        #go through the hidden scripts
        for sprite, script in KelpPlugin.iter_sprite_hidden_scripts(scratch):
            if not script.reachable:
                self.types["dead"][sprite]["hidden"].add(script)
            elif KelpPlugin.script_start_type(script) in self.types.keys():
                self.types[KelpPlugin.script_start_type(script)][sprite]["hidden"].add(script)

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)
        KelpPlugin.get_thumbnails(scratch)
        self.ScriptsType(scratch)
        self.EventsDisplay(self.thumbnails, self.types)

    def htmlview(self, sprites, event, fil):
        for sprite in sprites:
            fil.write('  <td>')
            visible = ""
            hidden = ""
            if event[sprite]['hidden']:
                for script in event[sprite]['hidden']:
                    hidden += KelpPlugin.to_scratch_blocks(sprite, script)
                fil.write('<pre class="hidden"><p>{0}</p></pre>'.format(hidden))
            if event[sprite]['visible']:
                for script in event[sprite]['visible']:
                    visible += KelpPlugin.to_scratch_blocks(sprite, script)
                fil.write('<pre class="blocks"><p>{0}</p></pre>'.format(visible))
            fil.write('  </td>')
        fil.write('  </tr>')


    def EventsDisplay(self, thumbnails, events):
        file = KelpPlugin.html_view("event", "Events")
        self.ScriptEventsDisplay(thumbnails, events, file)
        self.ThumbnailDisplay(thumbnails['screen'], file)
        file.write('</body>')
        file.write('</html>')
        file.close()



    def ScriptEventsDisplay(self, thumbnails, events, fil):
        # Displays sprite names and pictures
        fil.write('<table border="1"><tr><th class=noBorder></th>')
        sprites = []
        for sprite in thumbnails.keys():
            if sprite != 'screen':
                sprites.append(sprite)
                fil.write('    <th>{0}</th>'.format(sprite))
        fil.write('</tr>  <tr><td class="noBorder" ></td>')
        for sprite in sprites:
            fil.write('    <td><img src="{0}"></td>'.format(thumbnails[sprite]))
        fil.write('</tr>')

        # Displays scripts
        fil.write('<tr><td class = "noBorder"> Green Flag Scripts</td>')
        self.htmlview(sprites, events[self.HAT_GREEN_FLAG], fil)
        fil.write('<tr><td class= "noBorder"> On Sprite Click scripts</td>')
        self.htmlview(sprites, events[self.HAT_MOUSE], fil)
        fil.write('<tr><td class= "noBorder"> Key Pressed scripts</td>')
        self.htmlview(sprites, events[self.HAT_KEY], fil)
        fil.write('</table>')

    def ThumbnailDisplay(self, screen, fil):
        ### Screen shot of level ###
        fil.write('    <h2> Screenshot of Octopi Project </h2>')
        fil.write('    <td><img src="{0}" height="240" width="320" border="1"></td>'.format(screen))

