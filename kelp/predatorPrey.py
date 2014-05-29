"""This plugin is for the Predator Prey Project & Sequence Lesson.

Run via:

    kelp <project file> sequential predator

"""

from __future__ import print_function
from collections import Counter, namedtuple
from kelpplugin import KelpPlugin
from itertools import chain
from pprint import pprint
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
OUTPUT_HEADER = False


def compute_intersections(start, end, data):
    for sprite_name, (sprite_pos, radius) in LOCATIONS.items():
        segment = start, end
        if seg_distance(segment, sprite_pos) < radius:
            data[sprite_name] += 1
    if end.x < -244 or end.x > 243:
        data['#invalid_x'] += 1
        end = Point(max(-244, min(243, end.x)), end.y)
    elif end.y < -183 or end.y > 183:
        data['#invalid_y'] += 1
        end = Point(end.x, max(-183, min(183, end.y)))


def normalize(value):
    """Convert boolean to 0 or 1 string."""
    if isinstance(value, bool):
        return '1' if value else '0'
    else:
        return str(value)


def seg_distance(seg, point):
    # find the distance between the point and line segment
    dx = seg[1].x - seg[0].x
    dy = seg[1].y - seg[0].y
    u = ((point.x - seg[0].x) * dx +
         (point.y - seg[0].y) * dy) / float(dx ** 2 + dy ** 2)
    u = max(0, min(u, 1))
    return math.sqrt((seg[0].x + u * dx - point.x) ** 2 +
                     (seg[0].y + u * dy - point.y) ** 2)


def move(position, orientation, distance):
    rad = math.radians(orientation)
    return Point(position.x + math.sin(rad) * distance,
                 position.y + math.cos(rad) * distance)


def rotate_to(src, dst):
    return (90 - math.degrees(math.atan2(dst.y - src.y, dst.x - src.x))) % 360


def dynamic_analysis(blocks, attrs, data):
    # net's position is initialized in a hidden script
    net_orientation = 90
    net_position = Point(-190, 72)
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
            net_orientation = rotate_to(net_position, next_position)
            compute_intersections(net_position, next_position, data)
            net_position = next_position
        elif name not in ('when this sprite clicked',):
            print('OTHER_COUNTER: {} ({})'.format(name))

    if 'snake' not in attrs:
        data['snake'] = ''

    return (('snake' not in attrs or data['snake'] < 1) and
            all(data[x] > 0 for x in ('bear', 'horse', 'zebra')))


class Base(KelpPlugin):
    """Base class for plugins of the predatorPrey variety."""

    def get_blocks_and_attrs(self, scratch):
        def initial_attributes(sprite):
            attrs = ('direction', 'position', 'is_visible', 'size')
            return {x: getattr(sprite, x) for x in attrs}

        def posfix(sprite):
            """This hack correctly returns the position of the sprite.

            This is needed because for whatever reason the student version of
            octopi saves sprites with some offset.

            """
            x1, y1, x2, y2 = scratch._original[1].submorphs[0].owner \
                .bounds.value
            assert x2 - x1 == 480
            assert y2 - y1 == 360
            return Point(sprite.position[0] - x1, sprite.position[1] - y1)

        data = {x: 0 for x in KEYS}

        # find the list of blocks for Net::OnMouseClicked
        attrs = {}
        for sprite in scratch.sprites:
            attrs[sprite.name.lower()] = initial_attributes(sprite)

        saved_net_pos = posfix(sprite)
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


class ByStudent(Base):
    """Keep track of information by student."""

    def __init__(self):
        """Additionally keep track of submissions by student."""
        super(ByStudent, self).__init__()
        self.by_student = {}
        self._prev = {}
        self._last_filename = None

    def info(self, filename):
        return filename.split('/')[-2:]

    def finalize(self):
        output_heading = True
        keys = None
        for student, results in sorted(self.by_student.items()):
            if keys is None:
                keys = sorted(results.keys())
                print(', '.join(['student'] + keys))
            print(', '.join([student] + [normalize(results[x]) for x in keys]))


class AllBlocks(ByStudent):
    """Output statistics on what blocks were used by student"""

    def analyze(self, scratch, filename, **kwargs):
        student, submission = self.info(filename)

        file_blocks = Counter()
        for script in self.net_scripts(scratch):
            for name, _, _ in self.iter_blocks(script.blocks):
                file_blocks[name] += 1

        if student not in self.by_student:
            self.by_student[student] = file_blocks
        else:
            self.by_student[student].update(file_blocks)

    def finalize(self):
        for student, results in self.by_student.items():
            sys.stdout.write(student + ' ')
            pprint(results.most_common())


class MovementType(ByStudent):
    BLOCKS = {'point in direction %s': 'abs_ori',
              'turn @turnLeft %s degrees': 'rel_ori',
              'turn @turnRight %s degrees': 'rel_ori',
              'point towards %s': 'oth_ori',
              'when this sprite clicked': None,
              '%s glide %s steps': 'abs_pos',
              'glide %s steps': 'abs_pos',
              'glide %s to %s': 'pos_ori',
              'glide to %s': 'pos_ori'}
    TYPES = ('abs_ori', 'rel_ori', 'oth_ori', 'abs_pos', 'pos_ori')


    def analyze(self, scratch, filename, **kwargs):
        assert self._last_filename < filename
        self._last_filename = filename

        student, submission = self.info(filename)
        student_data = self.by_student.setdefault(student, {})
        if not student_data:  # Initialize the data on first submission
            student_data['attempts'] = 0
            for block_type in self.TYPES:
                student_data[block_type] = 0
                student_data['{}_all'.format(block_type)] = 0
        passed = student_data.get('passed', False)
        if not passed:
            student_data['attempts'] += 1

        # Determine if it worked as expected
        blocks, attrs, data = self.get_blocks_and_attrs(scratch)
        if not passed:
            student_data['passed'] = dynamic_analysis(blocks, attrs, data)

        all_type_counts = {x: 0 for x in self.TYPES}
        upto_last_counts = {x: 0 for x in self.TYPES}

        # For all blocks use the following
        #blocks = list(chain.from_iterable(self.iter_blocks(x.blocks) for x
        #                                  in self.net_scripts(scratch)))

        for name, _, _ in blocks:
            block_type = self.BLOCKS[name]
            if block_type:
                all_type_counts[block_type] += 1
                if not passed:
                    upto_last_counts[block_type] += 1

        for block_type, count in all_type_counts.items():
            student_data['{}_all'.format(block_type)] += count > 0

        if passed:  # Don't need to update the following values
            return

        for block_type, count in upto_last_counts.items():
            student_data[block_type] += count > 0
            student_data['{}_last'.format(block_type)] = count > 0


class PostPassed(ByStudent):
    """Plugin to inspect changes made once a correct solution was created.

    Excludes students who used glide_to.

    """
    BLOCKS = ('glide %s to %s', 'glide to %s')

    def analyze(self, scratch, filename, **kwargs):
        sys.stderr.write('.')
        sys.stderr.flush()
        assert self._last_filename < filename
        self._last_filename = filename

        student, submission = self.info(filename)
        passed = student in self.by_student and \
            self.by_student[student].get('passed', False)

        # Fetch blocks and attrs
        blocks, attrs, data = self.get_blocks_and_attrs(scratch)

        # Don't include if the blocks did not change
        if student in self._prev and self._prev[student] == blocks:
            return
        self._prev[student] = blocks

        glide_to = any(x[0] for x in blocks if x[0] in self.BLOCKS)
        if glide_to:  # Skip submission if they used glide to
            return

        # Determine if it worked as expected
        cur_passed = dynamic_analysis(blocks, attrs, data)

        if passed:
            self.by_student[student]['post_submissions'] += 1

        if cur_passed and not passed:
            student_data = {'passed':True, 'post_submissions': 0,
                            'post_passed': 0}
            self.by_student[student] = student_data
        elif passed:
            self.by_student[student]['post_passed'] += int(cur_passed)

        if cur_passed or passed:
            count = self.by_student[student]['post_submissions']
            with open('blocks/{}_{}.txt'.format(student, count), 'w') as fp:
                fp.write('{} {} {}\n'.format(student, submission, cur_passed))
                self.output(scratch, fp)

    def finalize(self):
        for student in self.by_student.keys():
            if self.by_student[student]['post_submissions'] == 0:
                del self.by_student[student]
            else:
                del self.by_student[student]['passed']
        super(PostPassed, self).finalize()


class Predator(Base):
    """Output statistics on the MammalsGame and AnimalsGame project."""

    def __init__(self):
        """Initialize and instance of the Predator plugin."""
        super(Predator, self).__init__()
        self.pass_count = 0

    def analyze(self, scratch, filename, **kwargs):
        # TODO: Verify initial position and orientation (other attributes too?)
        blocks, attrs, data = self.get_blocks_and_attrs(scratch)
        # Determine if it worked as expected
        passed = dynamic_analysis(blocks, attrs, data)

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
