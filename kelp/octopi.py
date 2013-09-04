"""A Kurt plugin for Octopi"""
from copy import copy, deepcopy

import kurt
from kurt.plugin import Kurt, KurtPlugin

# Import the shared functions from the scratch14 plugin
from kurt.scratch14 import Serializer, get_blocks_by_id
from kurt.scratch14.heights import clean_up
from kurt.scratch14.blocks import make_blocks
from kurt.scratch14.user_objects import (user_objects_by_name, UserObjectDef,
                                         make_user_objects)

# kurt_* -- objects from kurt 2.0 api
# v14_*  -- objects from the kurt.scratch14 module
# octopi*  -- objects from this module, octopi

#override the version in kurt.scratch14.blocks
squeak_sprite_blockspecs = """'motion' ('move %n steps' #- #forward:) ('glide %n steps' #t #forward:elapsed:from: 10) ('turn cw %n degrees' #- #turnRight: 15) ('turn ccw %n degrees' #- #turnLeft: 15) #- ('point in direction %d' #- #heading: 90) ('point towards %m' #- #pointTowards:) #- ('go to x:%n y:%n' #- #gotoX:y: 0 0) ('go to %m' #- #gotoSpriteOrMouse:) ('glide %n secs to x:%n y:%n' #t #glideSecs:toX:y:elapsed:from: 1 50 50) #- ('change x by %n' #- #changeXposBy: 10) ('set x to %n' #- #xpos: 0) ('change y by %n' #- #changeYposBy: 10) ('set y to %n' #- #ypos: 0) #- ('if on edge, bounce' #- #bounceOffEdge) #- ('x position' #r #xpos) ('y position' #r #ypos) ('direction' #r #heading) 'pen' ('clear' #- #clearPenTrails) #- ('pen down' #- #putPenDown) ('pen up' #- #putPenUp) #- ('set pen color to %c' #- #penColor:) ('change pen color by %n' #- #changePenHueBy:) ('set pen color to %n' #- #setPenHueTo: 0) #- ('change pen shade by %n' #- #changePenShadeBy:) ('set pen shade to %n' #- #setPenShadeTo: 50) #- ('change pen size by %n' #- #changePenSizeBy: 1) ('set pen size to %n' #- #penSize: 1) #- ('stamp' #- #stampCostume) 'looks' ('switch to costume %l' #- #lookLike:) ('next costume' #- #nextCostume) ('costume #' #r #costumeIndex) #- ('say %s for %n secs' #t #say:duration:elapsed:from: 'Hello!' 2) ('say %s' #- #say: 'Hello!') ('think %s for %n secs' #t #think:duration:elapsed:from: 'Hmm...' 2) ('think %s' #- #think: 'Hmm...') #- ('change %g effect by %n' #- #changeGraphicEffect:by: 'color' 25) ('set %g effect to %n' #- #setGraphicEffect:to: 'color' 0) ('clear graphic effects' #- #filterReset) #- ('change size by %n' #- #changeSizeBy:) ('set size to %n%' #- #setSizeTo: 100) ('size' #r #scale) #- ('show' #- #show) ('hide' #- #hide) #- ('go to front' #- #comeToFront) ('go back %n layers' #- #goBackByLayers: 1) 'sensing' ('touching %m?' #b #touching:) ('touching color %C?' #b #touchingColor:) ('color %C is touching %C?' #b #color:sees:) #- ('ask %s and wait' #s #doAsk 'What''s your name?') ('answer' #r #answer) #- ('mouse x' #r #mouseX) ('mouse y' #r #mouseY) ('mouse down?' #b #mousePressed) #- ('key %k pressed?' #b #keyPressed: 'space') #- ('distance to %m' #r #distanceTo:) #- ('reset timer' #- #timerReset) ('timer' #r #timer) #- ('%a of %m' #r #getAttribute:of:) #- ('loudness' #r #soundLevel) ('loud?' #b #isLoud) #~ ('%H sensor value' #r #sensor: 'slider') ('sensor %h?' #b #sensorPressed: 'button pressed')"""  # noqa


block_list = (
    list(make_blocks(kurt.scratch14.blockspecs_src.squeak_blockspecs)) +
    list(make_blocks(kurt.scratch14.blockspecs_src.squeak_stage_blockspecs)) +
    list(make_blocks(squeak_sprite_blockspecs)) +
    list(make_blocks(kurt.scratch14.blockspecs_src.squeak_obsolete_blockspecs))
    )

#taken directly from kurt.scratch14
block_list += [
    # variable reporters
    kurt.PluginBlockType('variables', 'reporter', 'readVariable',
                         [kurt.Insert('inline', 'var', default='var')]),
    kurt.PluginBlockType('variables', 'reporter', 'contentsOfList:',
                         [kurt.Insert('inline', 'list', default='list')]),

    # Blocks with different meaning depending on arguments are special-cased
    # inside load_block/save_block.
    kurt.PluginBlockType('control', 'hat', 'whenGreenFlag',
                         ['when green flag clicked']),
    kurt.PluginBlockType('control', 'hat', 'whenIReceive',
                         ['when I receive ', kurt.Insert('readonly-menu',
                                                         'broadcast')]),

    # changeVariable is special-cased (and isn't in blockspecs)
    kurt.PluginBlockType('variables', 'stack', 'changeVar:by:',
                         ['change ', kurt.Insert('readonly-menu', 'var'),
                          ' by ', kurt.Insert('number')]),
    kurt.PluginBlockType('variables', 'stack', 'setVar:to:',
                         ['set ', kurt.Insert('readonly-menu', 'var'),
                          ' to ', kurt.Insert('string')]),

    # MouseClickEventHatMorph is special-cased as it has an extra argument:
    # 'when %m clicked'
    kurt.PluginBlockType('control', 'hat', 'whenClicked',
                         ['when clicked']),
    ]


#override the version in kurt.scratch14.user_objects
user_obj = copy(user_objects_by_name)
scriptable_vars = (user_objects_by_name['ScriptableScratchMorph']
                   .defaults.copy())
scriptable_vars['hiddenbin'] = []
scriptable_vars['palettedict'] = {}
scriptable_vars['hidden'] = False
user_obj['ScriptableScratchMorph'] = UserObjectDef(1, 'BaseMorph',
                                                   scriptable_vars)
user_obj['ScratchStageMorph'] = UserObjectDef(
    7, 'ScriptableScratchMorph',
    user_objects_by_name['ScratchStageMorph'].defaults.copy())
user_obj['ScratchSpriteMorph'] = UserObjectDef(
    5, 'ScriptableScratchMorph',
    user_objects_by_name['ScratchSpriteMorph'].defaults.copy())
user_obj['BlockMorph'] = UserObjectDef(
    3, 'BaseMorph', [('isSpecialForm', None), ('oldColor', None),
                     ('hidden', False), ('inPalette', True)])

#below aren't mine - weird!
#user_obj['ChoiceArgMorph'] =  UserObjectDef(2, 'BaseMorph')
#user_obj['ExpressionArgMorphWithMenu'] =  UserObjectDef(2, 'BaseMorph')
#user_obj['ReporterBlockMorph'] =  UserObjectDef(
#    2, 'BaseMorph', [('isBoolean', False)])


class OctopiSerializer(Serializer):
    """Use one instance of Serializer for each load/save operation."""
    def load_scriptable(self, kurt_scriptable, voct_scriptable):
        Serializer.load_scriptable(self, kurt_scriptable, voct_scriptable)
        # hidden
        if isinstance(kurt_scriptable, kurt.Sprite):
            kurt_scriptable.hidden = voct_scriptable.hidden
        # palettedict
        kurt_scriptable.palette = deepcopy(voct_scriptable.palettedict)
        # hidden scripts
        kurt_scriptable.hiddenscripts = map(self.load_script,
                                            voct_scriptable.hiddenbin)
        # fix comments
        comments = []
        blocks_by_id = []
        # A list of all the blocks in script order but reverse script
        # blocks order.
        # Used to determine which block a Comment is anchored to.
        #
        # Note that Squeak arrays are 1-based, so index with:
        # blocks_by_id[index - 1]
        for script in kurt_scriptable.hiddenscripts:
            if isinstance(script, kurt.Comment):
                comments.append(script)
            elif isinstance(script, kurt.Script):
                for block in reversed(list(
                        kurt.scratch14.get_blocks_by_id(script))):
                    blocks_by_id.append(block)

        attached_comments = []
        for comment in comments:
            if hasattr(comment, '_anchor'):
                # Attach the comment to the right block from the given scripts.
                block = blocks_by_id[comment._anchor - 1]
                block.comment = comment.text
                attached_comments.append(comment)

        for comment in attached_comments:
            kurt_scriptable.hiddenscripts.remove(comment)

    def save_scriptable(self, kurt_scriptable, voct_scriptable):
        # save the visible scripts
        Serializer.save_scriptable(self, kurt_scriptable, voct_scriptable)
        # save the hidden scripts
        clean_up(kurt_scriptable.hiddenscripts)
        voct_scriptable.hiddenbin = map(self.save_script,
                                        kurt_scriptable.hiddenscripts)
        blocks_by_id = []
        for script in kurt_scriptable.hiddenscripts:
            if isinstance(script, kurt.Script):
                for block in reversed(list(get_blocks_by_id(script))):
                    blocks_by_id.append(block)

        def grab_comments(block):
            if block.comment:
                (x, y) = voct_scriptable.hiddenscripts[-1][0]
                pos = (x, y + 29)
                array = self.save_script(kurt.Comment(block.comment, pos),
                                         self.v14_project)
                for i in xrange(len(blocks_by_id)):
                    if blocks_by_id[i] is block:
                        array[1][0].append(i + 1)
                        break
                voct_scriptable.hiddenbin.append(array)

            for arg in block.args:
                if isinstance(arg, kurt.Block):
                    grab_comments(arg)
                elif isinstance(arg, list):
                    map(grab_comments, arg)

        for script in kurt_scriptable.hiddenscripts:
            if isinstance(script, kurt.Script):
                for block in script.blocks:
                    grab_comments(block)

        # save hidden and palettedict
        voct_scriptable.hidden = False  # default
        voct_scriptable.palettedict = kurt_scriptable.palettedict
        # sprite
        if isinstance(kurt_scriptable, kurt.Sprite):
            voct_scriptable.hidden = kurt_scriptable.hidden


class OctopiPlugin(KurtPlugin):
    name = 'octopi'
    display_name = 'Octopi from Scratch 1.4'
    extension = '.oct'
    features = []
    serializer_cls = OctopiSerializer
    blocks = block_list
    user_objects = make_user_objects(user_obj)

    def load(self, fp):
        return self.serializer_cls(self).load(fp)

    def save(self, fp, project):
        return self.serializer_cls(self).save(fp, project)


Kurt.register(OctopiPlugin())
