import kurt
import os
from hairball.plugins import HairballPlugin

BASE_PATH = './results'

class KelpPlugin(HairballPlugin):

    """The simple plugin name should go on the first comment line.

    The plugin description should start on the third line and can span as many
    lines as needed, though all newlines will be treated as a single space.

    If you are seeing this message it means you need to define a docstring for
    your plugin.

    """

    BLOCKMAPPING = {
        'costume': frozenset([('switch backdrop to %s', 'absolute'),
                              ('next backdrop', 'relative'),
                              ('switch costume to %s', 'absolute'),
                              ('next costume', 'relative')]),
        'orientation': frozenset([('turn @turnRight %s degrees', 'relative'),
                                  ('turn @turnLeft %s degrees', 'relative'),
                                  ('point in direction %s', 'absolute'),
                                  ('point towards %s', 'relative')]),
        'position': frozenset([('move %s steps', 'relative'),
                               ('glide %s steps', 'relative'),
                               ('go to x:%s y:%s', 'absolute'),
                               ('go to %s', 'relative'),
                               ('glide %s secs to x:%n y:%n', 'relative'),
                               ('change x by %s', 'relative'),
                               ('x position', 'absolute'),
                               ('change y by %s', 'relative'),
                               ('y position', 'absolute')]),
        'size': frozenset([('change size by %s', 'relative'),
                           ('set size to %s%%', 'absolute')]),
        'visibility': frozenset([('hide', 'absolute'),
                                 ('show', 'absolute')])}

    @classmethod
    def html_view(cls, file_name, title):
        file = open('results/{0}.html'.format(file_name), 'w')
        file.write('<html>')
        file.write('<head>')
        file.write('<meta charset="utf8">')
        file.write('<title>{0}</title>'.format(title))

        #<!-- Include jQuery -->
        file.write('<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>')

        #<!-- Include scratchblocks2 files -->
        file.write('<link rel="stylesheet" href="//charlottehill.com/scratchblocks/build/scratchblocks2.css">')
        file.write('<link rel="stylesheet" type="text/css" href="style.css">')
        file.write('<script src="//charlottehill.com/scratchblocks/build/scratchblocks2.js"></script>')

        #<!-- Parse blocks -->
        file.write('<script>')
        file.write('$(document).ready(function() {')
        file.write('     scratchblocks2.parse("pre.blocks");')
        file.write('     scratchblocks2.parse("pre.hidden");')
        file.write('     scratchblocks2.parse("pre.error");')
        file.write('     });')
        file.write('</script>')
        file.write('</script>')
        file.write('</head>')
        return file

    @staticmethod
    def iter_scripts(scratch):
        """A generator for all scripts contained in an octopi file.

        yields stage scripts first, then scripts for each sprite

        """
        for script in scratch.stage.scripts:
            if not isinstance(script, kurt.Comment):
            	yield script
        for script in scratch.stage.hiddenscripts:
            if not isinstance(script, kurt.Comment):
            	yield script
        for sprite in scratch.sprites:
            for script in sprite.scripts:
            	if not isinstance(script, kurt.Comment):
                    yield script
            for script in sprite.hiddenscripts:
            	if not isinstance(script, kurt.Comment):
                    yield script

    @staticmethod
    def iter_sprite_scripts(scratch):
        """A generator for all scripts contained in a scratch file.

        yields stage scripts first, then scripts for each sprite

        """
        for script in scratch.stage.scripts:
            if not isinstance(script, kurt.Comment):
            	yield ('Stage', script)
        for script in scratch.stage.hiddenscripts:
            if not isinstance(script, kurt.Comment):
            	yield ('Stage', script)
        for sprite in scratch.sprites:
            for script in sprite.scripts:
            	if not isinstance(script, kurt.Comment):
                    yield (sprite.name, script)
            for script in sprite.hiddenscripts:
            	if not isinstance(script, kurt.Comment):
                    yield (sprite.name, script)

    @staticmethod
    def iter_sprite_hidden_scripts(scratch):
        """A generator for all scripts contained in a scratch file.

        yields stage scripts first, then scripts for each sprite

        """
        for script in scratch.stage.hiddenscripts:
            if not isinstance(script, kurt.Comment):
            	yield ('Stage', script)
        for sprite in scratch.sprites:
            for script in sprite.hiddenscripts:
            	if not isinstance(script, kurt.Comment):
                    yield (sprite.name, script)

    @staticmethod
    def iter_sprite_visible_scripts(scratch):
        """A generator for all scripts contained in a scratch file.

        yields stage scripts first, then scripts for each sprite

        """
        for script in scratch.stage.scripts:
            if not isinstance(script, kurt.Comment):
            	yield ('Stage', script)
        for sprite in scratch.sprites:
            for script in sprite.scripts:
            	if not isinstance(script, kurt.Comment):
                    yield (sprite.name, script)


    @staticmethod
    def save_png(projectName, image, image_name, sprite_name=''):
        # Creates the name of the picture based on the sprites name
        pictureName = '{0}{1}.png'.format(sprite_name, image_name).replace('/', '_')
        # Stores the name of the project
        partialPath = '{0}'.format(projectName)
        # Creates the name of the path to the folder to store the pictures
        folder = os.path.join(BASE_PATH, partialPath + 'Pictures')
        # Creates the name of the path to store pictures based on the project's name
        path = os.path.join(BASE_PATH, partialPath + 'Pictures', pictureName)
        # If the folder does not exist yet, create it
        if not os.path.exists(folder):
            os.makedirs(folder)
        # Saves image as a ping to the specified pathway
        image.save(path)
        #        os.chmod(path, 0444)  # Read-only archive file
        # Must be world readable for NGINX to serve the file.
        return path

    @classmethod
    def tag_reachable_scripts(cls, scratch):
        """Tag each script with attribute reachable.

        The reachable attribute will be set false for any script that does not
        begin with a hat block. Additionally, any script that begins with a
        `when I receive` block whose event-name doesn't appear in a
        corresponding broadcast block is marked as unreachable.

        """
        scratch.kelp_prepared = True
        reachable = set()
        untriggered_events = {}
        # Initial pass to find reachable and potentially reachable scripts
        for script in cls.iter_scripts(scratch):
            if not isinstance(script, kurt.Comment):
            	starting_type = HairballPlugin.script_start_type(script)
            	if starting_type == HairballPlugin.NO_HAT:
                    script.reachable = False
            	elif starting_type == HairballPlugin.HAT_WHEN_I_RECEIVE:
                    script.reachable = False  # Value will be updated if reachable
                    message = script.blocks[0].args[0].lower()
                    untriggered_events.setdefault(message, set()).add(script)
            	else:
                    script.reachable = True
                    reachable.add(script)
        # Expand reachable states based on broadcast events
        while reachable:
            for event in HairballPlugin.get_broadcast_events(reachable.pop()):
                if event in untriggered_events:
                    for script in untriggered_events.pop(event):
                        script.reachable = True
                        reachable.add(script)

    @classmethod
    def get_thumbnails(cls, scratch):
        # Stores the name of the project
        projectName = scratch.name
        
        KelpPlugin.thumbnails = dict()
        KelpPlugin.thumbnails['Stage'] = KelpPlugin.save_png(projectName, scratch.stage.backgrounds[0], 'Stage');
        KelpPlugin.thumbnails['screen'] = KelpPlugin.save_png(projectName, scratch.thumbnail, 'screen');
        for sprite in scratch.sprites:
            KelpPlugin.thumbnails[sprite.name] = KelpPlugin.save_png(projectName, sprite.costumes[0], sprite.name)

    @classmethod
    def to_scratch_blocks(cls, heading, scripts):
        """Output the scripts in an html-ready scratch blocks format."""
        data = []
        for script in scripts:
            data.append('{0}\n'.format(script.stringify(True)))
        return ('<div>{0}</div>\n<div class="clear"></div>\n' '</div>\n').format(''.join(data))

