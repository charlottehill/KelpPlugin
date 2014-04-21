from hairball.plugins import HairballPlugin
import kurt
import os


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

    SCRIPT_TITLES = {
        HairballPlugin.HAT_GREEN_FLAG: 'When green flag clicked scripts',
        HairballPlugin.HAT_WHEN_I_RECEIVE: 'When I receive a message scripts',
        HairballPlugin.HAT_KEY: 'When a key is pressed scripts',
        HairballPlugin.HAT_MOUSE: 'When this sprite is clicked scripts',
        HairballPlugin.NO_HAT: ('Scripts without starting control blocks '
                                '(incomplete)')}

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

    @classmethod
    def to_scratch_blocks(cls, heading, scripts):
        """Output the scripts in an html-ready scratch blocks format."""
        data = []
        for script in scripts:
            data.append('{0}\n'.format(script.stringify(True)))
        return ('<div>{0}</div>\n<div class="clear"></div>\n' '</div>\n'
                .format(''.join(data)))

    @staticmethod
    def get_paths(image, project_name, image_name, sprite_name):
        directory = os.path.join('{}images'.format(project_name))
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = '{0}{1}.png'.format(sprite_name,
                                       image_name).replace('/', '_')
        path = os.path.join(directory, filename)
        return path, path

    def save_png(self, projectName, image, image_name, sprite_name=''):
        path, url = self.get_paths(image, projectName, image_name, sprite_name)
        image.save(path)
        return url

    def thumbnails(self, scratch):
        thumbnails = dict()
        thumbnails['Stage'] = self.save_png(scratch.name,
                                            scratch.stage.backgrounds[0],
                                            'Stage')
        thumbnails['screen'] = self.save_png(scratch.name,
                                             scratch.thumbnail, 'screen')
        for sprite in scratch.sprites:
            thumbnails[sprite.name] = self.save_png(scratch.name,
                                                    sprite.costumes[0],
                                                    sprite.name)
        return thumbnails
