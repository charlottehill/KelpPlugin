"""This plugin is for Lesson 3C: Initialization."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
from eventViewer import Events
import os
import sys
import kurt

'''How to run this plugin:
    hairball -d. -p initializationViewer.Initialization test.sb
'''

BASE_PATH = './results'
fil = open('initialization.html', 'w')

def partition_scripts(scripts, start_type):
    """Return two lists of scripts out of the original `scripts` list.

        Scripts that begin with a `start_type` block are returned first. All other
        scripts are returned second.

        """
    match, other = [], []
    for script in scripts:
        if KelpPlugin.script_start_type(script) == start_type:
            match.append(script)
        else:
            other.append(script)
    return match, other

class Initialization(KelpPlugin):

    STATE_NOT_MODIFIED = 0
    STATE_MODIFIED = 1
    STATE_INITIALIZED = 2


    def __init__(self):
        super(Initialization, self).__init__

    def attribute_state(self, sprite, scripts, attribute):
        """Return the state of the scripts for the given attribute.

            If there is more than one `when green flag clicked` script and they
            both modify the attribute, then the attribute is considered to not be
            initialized.

            """
        green_flag, other = partition_scripts(scripts, self.HAT_GREEN_FLAG)
        block_set = KelpPlugin.BLOCKMAPPING[attribute]
        state = self.STATE_NOT_MODIFIED
        # TODO: Any regular broadcast blocks encountered in the initialization
        # zone should be added to this loop for conflict checking.
        for script in green_flag:
            in_zone = True
            for name, level, block in self.iter_blocks(script.blocks):
                if name == 'broadcast %e and wait':
                    # TODO: Follow the broadcast and wait scripts that occur in
                    # the initialization zone
                    in_zone = False
                if (name, 'absolute') in block_set:
                    #print(name)
                    if in_zone and level == 0:  # Success!
                        if state == self.STATE_NOT_MODIFIED:
                            state = self.STATE_INITIALIZED
                        else:  # Multiple when green flag clicked conflict
                            state = self.STATE_MODIFIED
                            self.changes[sprite][attribute].append((block, script))
                    elif in_zone:
                        continue  # Conservative ignore for nested absolutes
                    else:
                        state = self.STATE_MODIFIED
                        self.changes[sprite][attribute].append((block, script))
                    break  # The state of the script has been determined
                elif (name, 'relative') in block_set:
                    state = self.STATE_MODIFIED
                    self.changes[sprite][attribute].append((block, script))
                    break
        if state != self.STATE_NOT_MODIFIED:
            return state
        # Check the other scripts to see if the attribute was ever modified
        for script in other:
            for name, _, block in self.iter_blocks(script.blocks):
                if name in [x[0] for x in block_set]:
                    self.changes[sprite][attribute].append((block, script))
                    state = self.STATE_MODIFIED
        return state


    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)

        # events
        self.events = Events()
        self.events.analyze(scratch)

        #initialization
        self.changes = dict()
        for sprite in scratch.sprites + [scratch.stage]:
            self.changes[sprite.name] = dict()
            for attr in self.BLOCKMAPPING.keys():
                self.changes[sprite.name][attr] = []
                self.attribute_state(sprite.name, sprite.scripts, attr)
        self.initializationDisplay(self.changes, self.events)

    def initializationDisplay(self, changes, events):
		file = KelpPlugin.html_view("Initialization", "Initialization")
        fil.write('<body>')

        events.ScriptEventsDisplay(events.thumbnails, events.types, fil)
        isEmpty = True
        for sprite in changes.keys():
        	for attr in changes[sprite].keys():
        		if changes[sprite][attr]:
        			isEmpty = False
        			break
        if not isEmpty:
       		self.InitScriptsDisplay(events.thumbnails, changes)

        fil.write('</body>')
        fil.write('</html>')
        fil.close()


    def InitScriptsDisplay(self, thumbnails, changes):
        # Displays sprite names and pictures
        fil.write('<h2> Uninitialized Scripts</h2>')
        fil.write('<table border="1">')
        fil.write('  <tr>')
        for sprite in thumbnails.keys():
            fil.write('    <th>{0}</th>'.format(sprite))
        fil.write('  </tr>  <tr>')
        for value in thumbnails.values():
            fil.write('    <td><img src="{0}" ></td>'.format(value))
        fil.write('  </tr>')
        # Displays uninitialized scripts
        fil.write('  <tr>')
        for sprite in thumbnails.keys():
            fil.write('  <td>')
            for type, list in changes[sprite].items():
                if list:
                    for block, script in list:
                        #This will display the problem block
                        fil.write('<pre class="error"><p>{0}\n</p></pre>'.format(block.stringify(True)))
                        #This will display the script that the block is in
                        fil.write('<pre class="blocks"><p>{0}</p></pre>'.format(KelpPlugin.to_scratch_blocks(sprite, script)))
            fil.write('  </td>')
        fil.write('  </tr></table>')
        return 0
