"""This plugin is for Lesson 3: Broadcast."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
from eventViewer import Events
import os
import sys
import kurt


'''How to run this plugin:
	hairball -k <path>/octopi.py -d <folder where sequenceViewer is> -p sequenceViewer.Sequence test.sb
	For example, if `octopi.py` and sequenceViewer are both in the directory where you are:
    hairball -k octopi.py -d . -p sequenceViewer.Sequence test.sb
    if sequenceViewer is in your directory but `octopi.py` is right outside of it:
    hairball -k ../octopi.py -d . -p sequenceViewer.Sequence test.sb
    If they're both right outside of it:
    hairball -k ../octopi.py -d .. -p sequenceViewer.Sequence test.sb
'''
class Broadcast(KelpPlugin):

    ATTRIBUTES = ('background', 'costume', 'orientation', 'position', 'size',
                  'visibility')

    STATE_NOT_MODIFIED = 0
    STATE_MODIFIED = 1
    STATE_INITIALIZED = 2


    def __init__(self):
        super(Broadcast, self).__init__

    def BroadcastIter(self, sc, e, sprite):
        """Given a script, return a set of scripts that are started by it"""
        messages = []
        for name, _, block in self.iter_blocks(sc):
            if 'broadcast %s' in name:
                if not isinstance(block.args[0], kurt.Block):
                    message = block.args[0].lower()
                    messages.append(message)
                    if message in self.broadcasts.keys():
                        self.broadcasts[message].append((sprite, sc))
                    else:
                        self.broadcasts[message] = [(sprite, sc)]
                    if message in self.receives.keys():
                        self.events[e].extend(self.receives[message])
                    else:
                        self.receives[message] = []
        for sprite, types in self.Events.types[self.HAT_WHEN_I_RECEIVE].items():
            for script in types['hidden'] | types['visible']:
            	message = script[0].args[0].lower()
                if message in messages:
                    if (sprite, script) not in self.events[e]:
                        self.receives[message].append((sprite, script))
                        self.events[e].append((sprite, script))
                        self.BroadcastIter(script, e, sprite)


        """Returns a dictionary of the scripts.
            Keys: start events
            Values: scripts that begin with those events ."""
    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)
        self.broadcasts = dict()
        self.receives = dict()
        self.events = dict()
        self.events[self.HAT_GREEN_FLAG] = []
        self.events[self.HAT_MOUSE] = []
        self.events[self.HAT_KEY] = []
        self.help = dict()
        self.help[self.HAT_GREEN_FLAG] = []
        self.help[self.HAT_MOUSE] = []
        self.help[self.HAT_KEY] = []

        addon = []
        """go through the scripts in each category. If we encounter a broadcast block,
            check for a corresponding when I receive. If there is, continue looking
            through that script for broadcast blocks. Add all connected     scripts to a set
            in the dictionary as (sprite, list of scripts) sets?"""

        self.Events = Events()
        self.Events.dir_path = self.dir_path  # HACK for image location
        self.Events.analyze(scratch)
        for e in self.events.keys():
            for sprite, types in self.Events.types[e].items():
                for script in types['visible'] | types['hidden']:
                    self.events[e].append((sprite,script))
                    self.BroadcastIter(script, e, sprite)
                    # Reorders the list for each tree for printing
                    extra = []
                    if not len(self.events[e]) == 1:
                        for sprite, script in self.events[e]:
                            for name, _, block in self.iter_blocks(script):
                                if 'broadcast %s' in name:
                                    if not (sprite, script) in extra:
                                        extra.append((sprite, script))
                                    addon = []
                                    br = False
                                    for sprite2, script2 in self.events[e]:
                                        if self.script_start_type(script2) == self.HAT_WHEN_I_RECEIVE:
                                            if block.args[0].lower() == script2[0].args[0].lower():
                                                for name3, _, _ in self.iter_blocks(script2):
                                                    if 'broadcast %s' in name3:
                                                        extra.append((sprite2,script2))
                                                        br = True
                                        if not br:
                                            if (sprite2,script2) not in extra:
                                                addon.append((sprite2,script2))
                                    extra.extend(addon)
                    	self.help[e].append(extra)
        return {'broadcast': self.help, 'thumbnails': self.thumbnails(scratch)}

def broadcast_display(results):
    broadcast = results['broadcast']
    thumbnails = results['thumbnails']
    html = []
    html.append('\n<h2 style="text-align:center;">Broadcast / Receive</h2>')
    message = ""
    for type, lists in broadcast.items():
        for list in lists:
            html.append('\n<hr>')
            html.append('\n<h2>{0}<h2>'.format(KelpPlugin.SCRIPT_TITLES[type])) #heading
            html.append('\n<table border = "1">')
            for sprite, script in list:
                if KelpPlugin.script_start_type(script) == KelpPlugin.HAT_WHEN_I_RECEIVE:
                    # check if the message is the same as the last one
                    # if it is, print this script next to the last
                    # otherwise, print it below the last
                    if message != script[0].args[0].lower():
                        html.append('\n  </tr>')
                        html.append('\n  <tr>')
                    message = script[0].args[0].lower()
                    script_images = KelpPlugin.to_scratch_blocks(sprite, script)
                    html.append('\n<td>')
                    html.append('\n<p>        {0}</p>'.format(sprite))
                    html.append('\n    <p><img src="{0}" height="100" width="100"></p>'.format(thumbnails[sprite]))
                    html.append('\n<pre class="blocks">')
                    html.append('\n<p>{0}</p>'.format(script_images))
                    html.append('\n</pre>')
                    html.append('\n</td>')
                elif KelpPlugin.script_start_type != KelpPlugin.NO_HAT:
                    if message == "":
                        html.append('\n  </tr>')
                    html.append('\n  <tr>')
                    script_images = KelpPlugin.to_scratch_blocks(sprite, script)
                    html.append('\n<p>{0}</p>'.format(sprite))
                    html.append('\n    <p><img src="{0}" height="100" width="100"></p>'.format(thumbnails[sprite]))
                    html.append('\n<pre class="blocks">')
                    html.append('\n<p>{0}</p>'.format(script_images))
                    html.append('\n</pre>')
                    html.append('\n  </tr>')
            html.append('\n</table>')
        return ''.join(html)

