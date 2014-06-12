"""This plugin is for the Predator Prey Project & Sequence Lesson.

Run via:

    kelp <project file> sequential predator

"""

from __future__ import print_function
from collections import Counter, namedtuple
from itertools import chain
from kelpplugin import KelpPlugin
import kurt
import math
import sys


Point = namedtuple('Point', ['x', 'y'])


DIRECTIONS = {'down': 180, 'left': -90, 'right': 90, 'up': 0}
KEYS = ('bear', 'horse', 'snake', 'zebra', '!scripts', '#blocks',
        '#blocks_other', '#extra_hat_mouse', '#glide', '#glide_to',
        '#invalid_dist', '#invalid_ori', '#invalid_point', '#invalid_target',
        '#invalid_x', '#invalid_y', '#unmoved', '#unrotated')
LOCATIONS = {'bear': (Point(51, 91), 100),
             'horse': (Point(128, -26), 90),
             'snake': (Point(134, -126), 50),
             'zebra': (Point(-143, -115), 100)}
NET_POSITION = Point(-190, 72)
OUTPUT_HEADER = False

APPROACH_BLOCKS = {'point in direction %s': 'abs_ori',
                   'turn @turnLeft %s degrees': 'rel_ori',
                   'turn @turnRight %s degrees': 'rel_ori',
                   'point towards %s': 'oth_ori',
                   'when this sprite clicked': None,
                   '%s glide %s steps': 'abs_pos',
                   'glide %s steps': 'abs_pos',
                   'glide %s to %s': 'pos_ori',
                   'glide to %s': 'pos_ori'}
APPROACH_TYPES = ('abs_ori', 'rel_ori', 'oth_ori', 'abs_pos', 'pos_ori')


def compute_intersections(start, end, data):
    assert start != end
    assert -244 <= end.x <= 243 and -183 <= end.y <= 183
    assert -244 <= start.x <= 243 and -183 <= start.y <= 183
    for sprite_name, (sprite_pos, radius) in LOCATIONS.items():
        if seg_distance((start, end), sprite_pos) < radius:
            data[sprite_name] += 1


def normalize(value):
    """Convert boolean to 0 or 1 string."""
    if isinstance(value, bool):
        return '1' if value else '0'
    elif isinstance(value, list):
        return ' '.join(str(x) for x in value)
    elif isinstance(value, set):
        return str(len(value))
    else:
        return str(value)


def point_distance(p1, p2):
    """Return the distance between two points."""
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)


def seg_distance(seg, point):
    """Return the minimum distance between the line segment and point."""
    assert seg[0] != seg[1]
    dx = seg[1].x - seg[0].x
    dy = seg[1].y - seg[0].y
    u = ((point.x - seg[0].x) * dx +
         (point.y - seg[0].y) * dy) / float(dx ** 2 + dy ** 2)
    u = max(0, min(u, 1))
    return point_distance(point, Point(seg[0].x + u * dx, seg[0].y + u * dy))


def move(position, orientation, distance):
    """Return the result of moving distance in orientation from position."""
    rad = math.radians(orientation)
    return Point(position.x + math.sin(rad) * distance,
                 position.y + math.cos(rad) * distance)


def rotate_to(src, dst):
    """Return the orientation necessary for src to point towards dst."""
    return (90 - math.degrees(math.atan2(dst.y - src.y, dst.x - src.x))) % 360


def dynamic_analysis(blocks, attrs, data):
    """Return the number of sprites picked up (excluding the snake)."""
    net_position = data.get('net_position', NET_POSITION)
    net_orientation = data.get('net_orientation', 90)
    initial_orientation = True

    # iterate through the script and calculate where the net goes
    for name, _, block in blocks:
        if name == 'point in direction %s':
            assert len(block.args) == 1
            prev_ori = net_orientation
            if block.args[0] in DIRECTIONS:
                net_orientation = DIRECTIONS[block.args[0]]
            else:
                try:
                    net_orientation = float(block.args[0])
                except ValueError:
                    data['#invalid_ori'] += 1
                    prev_ori = None  # Don't count as unrotated
            if not initial_orientation and prev_ori == net_orientation:
                data['#unrotated'] += 1
            initial_orientation = False
        elif name == 'turn @turnRight %s degrees':
            assert len(block.args) == 1
            if float(block.args[0]) == 0:
                data['#unrotated'] += 1
            net_orientation += float(block.args[0])
        elif name == 'turn @turnLeft %s degrees':
            assert len(block.args) == 1
            if float(block.args[0]) == 0:
                data['#unrotated'] += 1
            net_orientation -= float(block.args[0])
        elif name in ('glide %s steps', '%s glide %s steps'):
            if name == 'glide %s steps':
                assert len(block.args) == 1
                distance = block.args[0]
            else:
                assert len(block.args) == 2
                distance = block.args[1]
            data['#glide'] += 1
            if not isinstance(distance, float):  # enforce bounds
                if distance > 610 or distance < -610:
                    data['#invalid_dist'] += 1
                    distance = cmp(distance, 0) * 610
            if distance == 0:
                data['#unmoved'] += 1
                continue
            next_position = move(net_position, net_orientation, distance)

            # Fix next position within boundaries
            if next_position.x < -244 or next_position.x > 243:
                data['#invalid_x'] += 1
                next_position = Point(max(-244, min(243, next_position.x)),
                                      next_position.y)
            if next_position.y < -183 or next_position.y > 183:
                data['#invalid_y'] += 1
                next_position = Point(next_position.x,
                                      max(-183, min(183, next_position.y)))
            if net_position == next_position:
                data['#unmoved'] += 1
                continue
            compute_intersections(net_position, next_position, data)
            net_position = next_position
        elif name == 'point towards %s':
            assert len(block.args) == 1
            if block.args[0] is None:
                data['#invalid_point'] += 1
                continue
            target = LOCATIONS[block.args[0].lower()][0]
            net_orientation = rotate_to(net_position, target)
        elif 'glide' in name:
            if name == 'glide to %s':
                assert len(block.args) == 1
                dst = block.args[0].lower() if block.args[0] else None
            else:
                assert len(block.args) == 2
                dst = block.args[1].lower() if block.args[1] else None
            data['#glide_to'] += 1
            if dst not in LOCATIONS:
                data['#invalid_target'] += 1
                continue
            next_position = LOCATIONS[dst][0]
            # Glide to does not actually change the orientation
            # net_orientation = rotate_to(net_position, next_position)
            if net_position == next_position:
                data['#unmoved'] += 1
                continue
            compute_intersections(net_position, next_position, data)
            net_position = next_position
        elif name not in ('when this sprite clicked',):
            print('OTHER_COUNTER: {} ({})'.format(name))

    # Save the computed final net position
    data['net_position'] = net_position
    data['net_orientation'] = net_orientation

    if 'snake' not in attrs:
        data['snake'] = ''
    return sum(data[x] > 0 for x in ('bear', 'horse', 'zebra'))


class Base(KelpPlugin):
    """Base class for plugins of the Mammals or Animals Game variety.

    This plugin is not used directly.

    """

    def get_blocks_and_attrs(self, scratch):
        def initial_attributes(sprite):
            attrs = ('direction', 'position', 'is_visible', 'size')
            return {x: getattr(sprite, x) for x in attrs}

        data = {x: 0 for x in KEYS}

        # find the list of blocks for Net::OnMouseClicked
        attrs = {}
        for sprite in scratch.sprites:
            attrs[sprite.name.lower()] = initial_attributes(sprite)

        blocks = []
        other_blocks = 0
        scripts = 0

        for script in self.net_scripts(scratch):
            scripts += 1
            if self.script_start_type(script) == self.HAT_MOUSE:
                tmp_blocks = blocks
                blocks = list(self.iter_blocks(script))
                if tmp_blocks:
                    # Use HAT_MOUSE script with the most blocks
                    if len(tmp_blocks) > len(blocks):
                        tmp_blocks, blocks = blocks, tmp_blocks
                        data['#extra_hat_mouse'] += 1
                    other_blocks += len(tmp_blocks)
            else:
                other_blocks += len(list(self.iter_blocks(script)))
        data['#blocks'] = len(blocks)
        data['#blocks_other'] = other_blocks
        data['!scripts'] = scripts

        return blocks, attrs, data

    def net_position_analysis(self, scratch, computed_net_position):
        """Return the location of the net or distance from computed."""

        def posfix(sprite):
            """This hack correctly returns the position of the sprite.

            This is needed because for whatever reason the student version of
            octopi saves sprites with some offset.

            """
            x1, y1, x2, y2 = scratch._original[1].submorphs[0].owner \
                .bounds.value
            assert x2 - x1 == 480
            assert y2 - y1 == 360
            return Point(sprite.position[0] - x1, sprite.position[1] + y1)

        # Determine if the Net is at the start or computed position
        saved_net_position = None
        for sprite in scratch.sprites:
            if sprite.name == 'Net':
                saved_net_position = posfix(sprite)
                break
        if not saved_net_position:
            return 'UNMOVED'
        start_distance = point_distance(saved_net_position, NET_POSITION)
        distance = point_distance(saved_net_position, computed_net_position)
        if computed_net_position == NET_POSITION:
            return 'UNMOVED'
        elif saved_net_position == NET_POSITION:
            return 'START'
        elif distance < 6:
            return 'COMPUTED'
        elif start_distance < 6:
            return 'CLOSE TO START'
        else:
            return '{:.04f}'.format(distance)

    def net_scripts(self, scratch):
        """Generate the scripts that belong to the Net sprite."""
        for sprite in scratch.sprites:
            if sprite.name == 'Net':
                # TODO: Hairball should not yield comments
                scripts = [x for x in sprite.scripts if
                           not isinstance(x, kurt.Comment)]
                for script in scripts:
                    yield script
                break

    def output(self, scratch, fp=sys.stdout):
        for sprite in sorted(scratch.sprites, key=lambda x: x.name):
            scripts = [x for x in sprite.scripts
                       if not isinstance(x, kurt.Comment)]
            if not scripts:
                continue
            fp.write('  {}\n'.format(sprite.name))
            for i, script in enumerate(scripts):
                fp.write('    Script {}\n'.format(i + 1))
                for block in script.blocks:
                    fp.write('      {}\n'.format(block))

    def unique_blocks(self, blocks):
        """Return the blocks that are different from what was provided."""
        provided = (
            (kurt.Block('whenClicked'),),
            (kurt.Block('heading:', 90), kurt.Block('heading:', u'right')),
            (kurt.Block('forward:elapsed:from:', 50),),
            (kurt.Block('heading:', 180), kurt.Block('heading:', u'down')),
            (kurt.Block('forward:elapsed:from:', 50),),
            (kurt.Block('forward:elapsed:from:', 50),),
            (kurt.Block('forward:elapsed:from:', 50),))
        start = 0
        while start < len(provided) and start < len(blocks):
            if blocks[start][2] not in provided[start]:
                break
            start += 1
        return blocks[start:]


class ByStudent(Base):
    """Keep track of information by student.

    This plugin is not used directly.

    """

    def __init__(self):
        """Additionally keep track of submissions by student."""
        super(ByStudent, self).__init__()
        self.by_student = {}
        self._prev = {}  # used by is_similar
        self._last_filename = None

    def info(self, filename):
        return filename.split('/')[-2:]

    def is_similar(self, student, blocks):
        """Return if the student's previous submission has the same blocks."""
        retval = student in self._prev and self._prev[student] == blocks
        self._prev[student] = blocks
        return retval

    def finalize(self):
        keys = None
        for student, results in sorted(self.by_student.items()):
            if keys is None:
                keys = sorted(results.keys())
                print(', '.join(['student'] + keys))
            print(', '.join([student] + [normalize(results[x]) for x in keys]))


class SnapshotChecker(ByStudent):
    MAMMALS = ('2013-11-14 11:18:27', 'save', 'MammalsGame')
    ANIMALS = ('2014-1-28 08:36:56', 'save', 'AnimalsGame')
    """Compare the number of snapshots with the number of saved files.

    This plugin is used to verify the accuracy of data collection.

    """
    def analyze(self, scratch, filename, **kwargs):
        def get_history():
            history = [tuple(x.strip().split('\t')) for x in
                       scratch._original[0]['history'].strip().split('\r')]
            try:
                return history[history.index(self.ANIMALS) + 1:]
            except ValueError:
                return history[history.index(self.MAMMALS) + 1:]

        student, submission = self.info(filename)

        student_data = self.by_student.setdefault(student, {})
        if not student_data:  # Initialize the data on first submission
            student_data['files'] = 0
            for attr in ('saves', 'snapshots'):
                student_data[attr] = set()
        history = get_history()
        snapshots = [x for x in history if '(' in x[2]]
        student_data['files'] += 1
        student_data['saves'] |= set(history)
        student_data['snapshots'] |= set(snapshots)


class DoubleClick(ByStudent):
    """Attempts to identify students using double click to execute."""
    def analyze(self, scratch, filename, **kwargs):
        student, submission = self.info(filename)
        student_data = self.by_student.setdefault(student, {})
        if not student_data:  # Initialize the data on first submission
            for attr in ('double_click', 'high_prob_1', 'high_prob_mult',
                         'start', 'invalid_pos', 'sprite_click'):
                student_data[attr] = 0
        if student_data.get('passed', False):
            # Ignore submissions after a passed submission
            return

        blocks, attrs, data = self.get_blocks_and_attrs(scratch)
        if self.is_similar(student, blocks):  # Skip similar submissions
            return

        if dynamic_analysis(blocks, attrs, data) > 1:
            # If at least two objects are picked up the student demonstrates
            # partial understanding
            student_data['passed'] = True
            return

        net = self.net_position_analysis(scratch, data['net_position'])
        if data['!scripts'] == 0:  # Ignore submissions with no scripts
            assert net == 'UNMOVED'
            return
        elif net == 'UNMOVED':
            if data['#blocks'] > 0 and data['!scripts'] == 1:
                # Ignore submissions with no movement and no unexpected scripts
                return
            elif data['!scripts'] == 1:
                student_data['high_prob_1'] += 1
            else:
                student_data['high_prob_mult'] += 1
        elif net == 'COMPUTED':
            assert data['net_position'] != NET_POSITION
            # If the net ends where we expect it then it is not double clicking
            return

        if net == 'START':
            student_data['start'] += 1
        elif net != 'UNMOVED':
            # Save
            invalid_pos = data['#invalid_x'] > 0 or data['#invalid_y'] > 0
            # Check if the net was clicked a up to N times
            for i in range(8):  # None occur more than 8 times
                if data['#invalid_x'] > 0 or data['#invalid_y'] > 0:
                    break
                if data['snake'] == '':  # Fix issues with snake reset
                    data['snake'] = 0
                dynamic_analysis(blocks, attrs, data)
                net = self.net_position_analysis(scratch, data['net_position'])
                if net == 'COMPUTED':
                    student_data['sprite_click'] += 1
                    return
            if invalid_pos:  # Increment invalid position count
                student_data['invalid_pos'] += 1
        student_data['double_click'] += 1  # Potential double clicking

    def finalize(self):
        for student in self.by_student.keys():
            tmp = self.by_student[student]
            if tmp['double_click'] == tmp['sprite_click'] == 0:
                del self.by_student[student]
            elif 'passed' not in tmp:
                tmp['passed'] = False
        super(DoubleClick, self).finalize()


class ApproachBySub(ByStudent):
    """Keep track of the approach used on an individual submission."""
    ORI_TYPES = set(['abs_ori', 'rel_ori', 'oth_ori'])

    def analyze(self, scratch, filename, **kwargs):
        student, submission = self.info(filename)
        blocks, attrs, data = self.get_blocks_and_attrs(scratch)
        counts = {x: 0 for x in APPROACH_TYPES}
        counts['Passed'] = dynamic_analysis(blocks, attrs, data) > 1

        prev_ori = None
        for name, _, _ in self.unique_blocks(blocks):
            block_type = APPROACH_BLOCKS[name]
            if block_type in self.ORI_TYPES:  # Save until glide DIST
                prev_ori = block_type
            elif block_type:
                counts[block_type] += 1
                if prev_ori and block_type == 'abs_pos':
                    counts[prev_ori] += 1
                    prev_ori = None

        self.by_student[(student, submission)] = counts

    def finalize(self):
        keys = None
        for (student, submission), results in sorted(self.by_student.items()):
            if keys is None:
                keys = sorted(results.keys())
                print(', '.join(['student', 'submission'] + keys))
            print(', '.join([student, submission]
                            + [normalize(results[x]) for x in keys]))


class Approaches(ByStudent):
    """Keep track of the approaches used by student."""
    ORI_TYPES = set(['abs_ori', 'rel_ori', 'oth_ori'])

    def analyze(self, scratch, filename, **kwargs):
        assert self._last_filename < filename
        self._last_filename = filename

        student, submission = self.info(filename)
        student_data = self.by_student.setdefault(student, {})
        if not student_data:  # Initialize the data on first submission
            student_data['attempts'] = 0
            for block_type in APPROACH_TYPES:
                student_data[block_type] = 0
                student_data['{}_all'.format(block_type)] = 0
        passed = student_data.get('passed', False)
        if not passed:
            student_data['attempts'] += 1

        # Determine if it worked as expected
        blocks, attrs, data = self.get_blocks_and_attrs(scratch)
        if not passed:
            student_data['passed'] = dynamic_analysis(blocks, attrs, data) > 1

        all_type_counts = {x: 0 for x in APPROACH_TYPES}
        upto_last_counts = {x: 0 for x in APPROACH_TYPES}

        # For all blocks use the following
        # blocks = list(chain.from_iterable(self.iter_blocks(x.blocks) for x
        #                                   in self.net_scripts(scratch)))

        prev_ori = None
        for name, _, _ in self.unique_blocks(blocks):
            block_type = APPROACH_BLOCKS[name]
            if block_type in self.ORI_TYPES:  # Save until glide DIST
                prev_ori = block_type
            elif block_type:
                all_type_counts[block_type] += 1
                if not passed:
                    upto_last_counts[block_type] += 1
                if prev_ori and block_type == 'abs_pos':
                    all_type_counts[prev_ori] += 1
                    if not passed:
                        upto_last_counts[prev_ori] += 1
                    prev_ori = None

        for block_type, count in all_type_counts.items():
            student_data['{}_all'.format(block_type)] += count > 0

        if passed:  # Don't need to update the following values
            return
        elif '{}_last'.format(APPROACH_TYPES[0]) in student_data \
                and sum(upto_last_counts.values()) == 0:
            # Only include empty submissions if there isn't already one
            return

        for block_type, count in upto_last_counts.items():
            student_data[block_type] += count > 0
            student_data['{}_last'.format(block_type)] = count > 0


class RaceCondition(ByStudent):
    """Plugin to detect potential race-condition issues with the Zebra."""
    FORWARD_50 = (kurt.Block('forward:elapsed:from:', 50),
                  kurt.Block('speed:forward:elapsed:from:', 'slow', 50),
                  kurt.Block('speed:forward:elapsed:from:', 'medium', 50),
                  kurt.Block('speed:forward:elapsed:from:', 'fast', 50))
    FORWARD_100 = (kurt.Block('forward:elapsed:from:', 100),
                   kurt.Block('speed:forward:elapsed:from:', 'slow', 100),
                   kurt.Block('speed:forward:elapsed:from:', 'medium', 100),
                   kurt.Block('speed:forward:elapsed:from:', 'fast', 100))
    FORWARD_150 = (kurt.Block('forward:elapsed:from:', 150),
                   kurt.Block('speed:forward:elapsed:from:', 'slow', 150),
                   kurt.Block('speed:forward:elapsed:from:', 'medium', 150),
                   kurt.Block('speed:forward:elapsed:from:', 'fast', 150))
    FORWARD_MANY = (kurt.Block('forward:elapsed:from:', 200),
                    kurt.Block('speed:forward:elapsed:from:', 'slow', 200),
                    kurt.Block('speed:forward:elapsed:from:', 'medium', 200),
                    kurt.Block('speed:forward:elapsed:from:', 'fast', 200),
                    kurt.Block('forward:elapsed:from:', 250),
                    kurt.Block('speed:forward:elapsed:from:', 'slow', 250),
                    kurt.Block('speed:forward:elapsed:from:', 'medium', 250),
                    kurt.Block('speed:forward:elapsed:from:', 'fast', 250),
                    kurt.Block('forward:elapsed:from:', 300),
                    kurt.Block('speed:forward:elapsed:from:', 'slow', 300),
                    kurt.Block('speed:forward:elapsed:from:', 'medium', 300),
                    kurt.Block('speed:forward:elapsed:from:', 'fast', 300))
    POINT_DOWN = kurt.Block('heading:', 180), kurt.Block('heading:', u'down')
    POINT_LEFT = kurt.Block('heading:', -90), kurt.Block('heading:', u'left')
    POINT_RIGHT = kurt.Block('heading:', 90), kurt.Block('heading:', u'right')
    POINT_UP = kurt.Block('heading:', 0), kurt.Block('heading:', u'up')
    POINT_TO_OTHER = (kurt.Block('pointTowards:', u'Horse'),
                      kurt.Block('pointTowards:', u'Bear'))
    POINT_TO_ZEBRA = kurt.Block('pointTowards:', u'Zebra')
    GLIDE_TO_ZEBRA = (kurt.Block('glidetoSpriteOrMouse:elapsed:from:',
                                 u'Zebra'),
                      kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'slow',
                                 u'Zebra'),
                      kurt.Block('glide:toSpriteOrMouse:elapsed:from:',
                                 'medium', u'Zebra'),
                      kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'fast',
                                 u'Zebra'))
    GLIDE_TO_OTH = (kurt.Block('glidetoSpriteOrMouse:elapsed:from:', u'Bear'),
                    kurt.Block('glidetoSpriteOrMouse:elapsed:from:', u'Horse'),
                    kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'slow',
                               u'Bear'),
                    kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'slow',
                               u'Horse'),
                    kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'medium',
                               u'Bear'),
                    kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'medium',
                               u'Horse'),
                    kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'fast',
                               u'Bear'),
                    kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'fast',
                               u'Horse'))
    NOP = (kurt.Block('heading:', None),
           kurt.Block('forward:elapsed:from:', 0),
           kurt.Block('glidetoSpriteOrMouse:elapsed:from:', None),
           kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'slow', None),
           kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'medium', None),
           kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'fast', None))
    INVALID = (kurt.Block('glidetoSpriteOrMouse:elapsed:from:',
                          'mouse-pointer'),
               kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'slow',
                          'mouse-pointer'),
               kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'medium',
                          'mouse-pointer'),
               kurt.Block('glide:toSpriteOrMouse:elapsed:from:', 'fast',
                          'mouse-pointer'))
    TURN_CCW_90 = kurt.Block('turnLeft:', 90)
    TURN_CW_90 = kurt.Block('turnRight:', 90)

    def is_match(self, blocks):
        state = 0  # Start
        block_num = 0
        while block_num < len(blocks):
            name, _, block = blocks[block_num]
            info = state, block_num, name
            prev_state = state
            # General exit conditions
            if block in self.INVALID:
                return 'invalid'

            if state == 0:
                if block != kurt.Block('whenClicked'):
                    return False
                state = 1
            elif state == 1:  # At start, pointing right
                if block in self.POINT_RIGHT:
                    prev_state = None
                elif block in chain([self.TURN_CCW_90], self.POINT_LEFT,
                                    self.POINT_UP, self.POINT_TO_OTHER):
                    state = 2  # May result in subsequent rotation
                elif block in self.FORWARD_50:
                    state = 3
                elif block in chain([self.POINT_TO_ZEBRA, self.TURN_CW_90],
                                    self.POINT_DOWN):
                    state = 4
                elif block in chain(self.FORWARD_100, self.FORWARD_150,
                                    self.FORWARD_MANY, self.GLIDE_TO_OTH,
                                    self.GLIDE_TO_ZEBRA):
                    return False  # Ignore commonly occuring sequence
            elif state == 2:  # At start pointing in useless direction
                if block in self.POINT_TO_OTHER:
                    prev_state = None  # Indicate handling
                elif block in self.POINT_RIGHT:
                    state = 1
                elif block in chain(self.POINT_DOWN, [self.POINT_TO_ZEBRA]):
                    state = 4
                elif block in chain(self.FORWARD_50, self.FORWARD_100,
                                    self.FORWARD_150, self.FORWARD_MANY,
                                    self.GLIDE_TO_OTH, self.GLIDE_TO_ZEBRA):
                    return False  # Ignore commonly occuring sequence
            elif state == 3:  # 50 steps to the left of start, pointing right
                if block in self.POINT_RIGHT:
                    prev_state = None  # Indicate handling
                elif block in chain([self.TURN_CW_90], self.POINT_DOWN):
                    state = 4
                elif block in chain(self.FORWARD_50, self.GLIDE_TO_OTH):
                    return False  # Handle common situation
            elif 4 <= state <= 6:
                # Pointing down, or towards zebra at some 50 step
                # interval below and/or to the right of the start
                if block in self.POINT_DOWN:
                    prev_state = None  # Indicate handling
                elif block in self.FORWARD_50:
                    state += 1
                elif block in self.FORWARD_100 and state < 6:
                    state += 2
                elif block in self.FORWARD_150 and state < 5:
                    state += 1
                elif block in self.GLIDE_TO_ZEBRA:
                    return 'post_glide'
                elif block in chain(self.FORWARD_100, self.FORWARD_150,
                                    self.FORWARD_MANY):
                    return 'fix'
                elif block in chain(self.GLIDE_TO_OTH, self.POINT_RIGHT):
                    return False  # Ignore commonly occuring sequence
            elif state == 7:  # Intersecting with the Zebra
                if block in chain([self.TURN_CW_90],
                                  self.POINT_DOWN, self.POINT_LEFT):
                    prev_state = None  # Indicate handling
                elif block in chain([self.TURN_CCW_90],
                                    self.POINT_RIGHT, self.POINT_UP,
                                    self.POINT_TO_OTHER):
                    return 'issue'
                elif block in self.GLIDE_TO_OTH:
                    return 'post_glide'
                elif block in self.GLIDE_TO_ZEBRA:
                    return 'fix'
                elif name == 'glide %s steps':
                    return 'fix'
            if prev_state == state and block not in self.NOP:
                # Unhandled situation
                self.by_student['_nexts'][info] += 1
                return False
            block_num += 1
        return 'initial' if state == 7 else False

    def analyze(self, scratch, filename, **kwargs):
        if '_nexts' not in self.by_student:  # First run only
            self.by_student['_nexts'] = Counter()

        student, submission = self.info(filename)
        student_data = self.by_student.setdefault(student, {})
        if 'issue' not in student_data:  # Initialize on student first
            for key in ('fix', 'initial', 'invalid', 'issue', 'passed',
                        'post_glide'):
                student_data[key] = []
            student_data['subs'] = 0
            student_data['matches'] = 0

        # Fetch blocks and attrs
        blocks, attrs, data = self.get_blocks_and_attrs(scratch)
        if self.is_similar(student, blocks):  # Skip similar submissions
            return
        student_data['subs'] += 1
        if dynamic_analysis(blocks, attrs, data) > 1:
            student_data['passed'].append(student_data['subs'])

        match = self.is_match(blocks)
        if match:
            student_data[match].append(student_data['subs'])
            student_data['matches'] += 1
            if match != 'invalid':
                assert data['zebra'] > 0

    def finalize(self):
        for value, count in self.by_student['_nexts'].items():
            if count >= 10:
                print(count, value)
        sys.stderr.write('Unhandled: {}\n'
                         .format(sum(self.by_student['_nexts'].values())))
        del self.by_student['_nexts']
        keys = None
        for student, results in sorted(self.by_student.items()):
            del results['subs']
            if keys is None:
                keys = sorted(results.keys())
                print(', '.join(['student'] + keys))
            print(', '.join([student] + [normalize(results[x]) for x in keys]))


class ClassStats(ByStudent):
    """Plugin to provide basic statistics based on a per-class basis."""
    def analyze(self, scratch, filename, **kwargs):
        student, submission = self.info(filename)

        class_name = student[:-2]
        if class_name not in self.by_student:
            class_data = {'subs': [0, 0, 0, 0],
                          'students': [set(), set(), set(), set()]}
            self.by_student[class_name] = class_data
        else:
            class_data = self.by_student[class_name]

        # Fetch blocks and attrs
        blocks, attrs, data = self.get_blocks_and_attrs(scratch)
        # Determine if it worked as expected
        sprites = dynamic_analysis(blocks, attrs, data)

        # Increment submission count
        class_data['subs'][sprites] += 1

        existing = None
        for i, num_set in enumerate(class_data['students']):
            if student in num_set:
                existing = i
        if existing is None:  # Always add
            class_data['students'][sprites].add(student)
        elif sprites > existing:  # Remove from former and add
            class_data['students'][existing].remove(student)
            class_data['students'][sprites].add(student)

    def finalize(self):
        def norm(data):
            if isinstance(data, set):
                return str(len(data))
            else:
                return str(data)
        attrs = ['subs_0', 'subs_1', 'subs_2', 'subs_3',
                 'students_0', 'students_1', 'students_2', 'students_3']
        print(', '.join(['class_name'] + attrs))
        for class_name, class_data in sorted(self.by_student.items()):
            print(', '.join([class_name] + [str(x) for x in class_data['subs']]
                            + [norm(x) for x in class_data['students']]))


class SnapshotInfo(Base):
    """Output statistics on the MammalsGame and AnimalsGame projects.

    This plugin is used to generate a heap of data about each snapshot, but
    is not used directly in any of the paper's graphs.

    """

    def __init__(self):
        """Initialize and instance of the Predator plugin."""
        super(SnapshotInfo, self).__init__()
        self.pass_count = 0

    def analyze(self, scratch, filename, **kwargs):
        # TODO: Verify initial position and orientation (other attributes too?)
        blocks, attrs, data = self.get_blocks_and_attrs(scratch)
        # Determine if it worked as expected
        passed = dynamic_analysis(blocks, attrs, data) > 1

        data['net'] = self.net_position_analysis(scratch, data['net_position'])
        del data['net_position']

        output = [normalize(x[1]) for x in sorted(data.items())]
        global OUTPUT_HEADER
        if not OUTPUT_HEADER:
            print(', '.join(['Student', 'Sub'] + sorted(data.keys())
                            + ['Passed']))
            OUTPUT_HEADER = True

        path_parts = filename.split('/')[-2:]
        if passed:
            self.pass_count += 1
        output[0:0] = path_parts
        output.append(normalize(passed))
        print(', '.join(output))
        return data

    def finalize(self):
        sys.stderr.write('{} passed\n'.format(self.pass_count))


def predator_display(seq):
    html = []
    negative = []
    for name, pickedup in seq.items():
        if name == 'Snake':
            if pickedup:
                negative.append('<h2 style="background-color:LightBlue">')
                negative.append('Are you sure that a snake is a mammal?</h2>')
            else:
                html.append('<h2 style="background-color:LightGreen">')
                html.append('Great job avoiding the snake!</h2>')
        else:
            if pickedup:
                html.append('<h2 style="background-color:LightGreen">')
                html.append('Great job picking up the {0}!</h2>'.format(name))
            else:
                negative.append('<h2 style="background-color:LightBlue">')
                negative.append('It looks like you didn\'t pick up the {0}. Is'
                                ' it a mammal?</h2>'.format(name))

    html.append('<br>')
    if len(negative) > 0:
        html.append('<h2>If you still have time...</h2>')
        html.extend(negative)
    else:
        html = []
        html.append('<h2 style="background-color:LightGreen">')
        html.append('Great job picking up all the mammals!</h2>')

    return ''.join(html)


if __name__ == '__main__':
    """Provide some tests for the plugin."""
    epsl = sys.float_info.epsilon * 2

    def test_similar(a, b):
        if abs(a.x - b.x) > epsl or abs(a.y - b.y) > epsl:
            print('{} is not similar to {}'.format(a, b))

    center = Point(0, 0)
    up = Point(0, 1)
    right = Point(1, 0)
    down = Point(0, -1)
    left = Point(-1, 0)
    assert rotate_to(center, up) == 0
    assert rotate_to(center, right) == 90
    assert rotate_to(center, down) == 180
    assert rotate_to(center, left) == 270

    # Verify that we can move properly
    test_similar(center, move(up, rotate_to(up, center), 1))
    test_similar(center, move(right, rotate_to(right, center), 1))
    test_similar(center, move(down, rotate_to(down, center), 1))
    test_similar(center, move(left, rotate_to(left, center), 1))

    test_similar(right, move(left, rotate_to(left, right), 2))
    test_similar(left, move(right, rotate_to(right, left), 2))
    test_similar(down, move(up, rotate_to(up, down), 2))
    test_similar(up, move(down, rotate_to(down, up), 2))

    test_similar(up, move(left, rotate_to(left, up), math.sqrt(2)))
    test_similar(up, move(right, rotate_to(right, up), math.sqrt(2)))

    test_similar(down, move(left, rotate_to(left, down), math.sqrt(2)))
    test_similar(down, move(right, rotate_to(right, down), math.sqrt(2)))
