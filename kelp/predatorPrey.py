"""This plugin is for the Predator Prey Project & Sequence Lesson.

Run via:

    kelp <project file> sequential predator

"""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
import kurt
import math


DIRECTIONS = {'down': 180, 'left': -90, 'right': 90, 'up': 0}
# locations of all the animals
LOCATIONS = {'bear': (51, 91), 'horse': (128, -26),
             'snake': (134, -126), 'zebra': (-143, -115)}

OUTPUT_HEADER = False


def normalize(value):
    if isinstance(value, bool):
        return '1' if value else '0'
    else:
        return str(value)


class Predator(KelpPlugin):
    """Output statistics on the MammalsGame and AnimalsGame project."""

    def __init__(self):
        """Initialize and instance of the Predator plugin."""
        super(Predator, self).__init__()
        self.other_counter = Counter()

    def analyze(self, scratch, filename, **kwargs):
        data = {'bear': False, 'horse': False, 'snake': False, 'zebra': False,
                '#extra_hat_mouse': 0,
                '#invalid_block': 0, '#invalid_dist': 0, '#invalid_ori': 0,
                '#unmoved': 0, '#unrotated': 0}

        # TODO: Verify initial position and orientation (other attributes too?)

        # find the list of blocks for Net::OnMouseClicked
        blocks = []
        for sprite in scratch.sprites:
            if sprite.name == 'Net':
                blocks = []
                other_blocks = 0

                # TODO: Hairball should not yield comments
                scripts = [x for x in sprite.scripts if
                           not isinstance(x, kurt.Comment)]

                for script in scripts:
                    start_type = self.script_start_type(script)
                    if start_type == self.HAT_MOUSE:
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
                data['#scripts'] = len(scripts)
                break

        # net's position is initialized in a hidden script
        x1, y1 = -190, 72
        x2, y2 = x1, y1
        direction = 90
        initial_orientation = True

        # iterate through the script and calculate where the net goes
        for name, _, block in blocks:
            if name == 'point in direction %s':
                assert len(block.args) == 1
                prev_direction = direction
                if block.args[0] in DIRECTIONS:
                    direction = DIRECTIONS[block.args[0]]
                else:
                    try:
                        direction = float(block.args[0])
                    except ValueError:
                        data['#invalid_ori'] += 1
                        prev_direction = None  # Don't count as unrotated
                if not initial_orientation and prev_direction == direction:
                    data['#unrotated'] += 1
                initial_orientation = False
            elif name == 'turn @turnRight %s degrees':
                assert len(block.args) == 1
                if float(block.args[0]) == 0:
                    data['#unrotated'] += 1
                direction = direction + float(block.args[0])
            elif name == 'turn @turnLeft %s degrees':
                assert len(block.args) == 1
                if float(block.args[0]) == 0:
                    data['#unrotated'] += 1
                direction = direction - float(block.args[0])
            elif name == 'glide %s steps':
                assert len(block.args) == 1
                distance = block.args[0]
                if not isinstance(block.args[0], float):  # enforce bounds
                    if distance > 250:
                        data['#invalid_dist'] += 1
                        distance = 250
                    elif distance < -250:
                        data['#invalid_dist'] += 1
                        distance = -250
                if distance == 0:
                    data['#unmoved'] += 1
                    continue
                # calculate next location
                rad = math.radians(direction)
                x2 = x1 + math.sin(rad) * distance
                y2 = y1 + math.cos(rad) * distance
                # check line
                for animal, (x3, y3) in LOCATIONS.items():
                    if not data[animal]:
                        # find the distance between the point and line segment
                        px = x2 - x1
                        py = y2 - y1
                        something = float(px*px + py*py)
                        u = ((x3 - x1) * px + (y3 - y1) * py) / something
                        if u > 1:
                            u = 1
                        elif u < 0:
                            u = 0
                        dx = x1 + u * px - x3
                        dy = y1 + u * py - y3
                        distance = math.sqrt(dx*dx + dy*dy)
                        # check if the distance between point and the line < 70
                        if distance < 70:
                            data[animal] = True
                x1, y1 = x2, y2
            elif 'glide' in name:
                data['#invalid_block'] += 1
            # TODO: handle point towards
            elif name not in ('when this sprite clicked',):
                self.other_counter[name] += 1

        output = [normalize(x[1]) for x in sorted(data.items())]
        global OUTPUT_HEADER
        if not OUTPUT_HEADER:
            print(', '.join(['Filename'] + sorted(data.keys()) + ['Passed']))
            OUTPUT_HEADER = True

        output.insert(0, '/'.join(filename.split('/')[-2:]))
        output.append(
            normalize(not data['snake'] and
                      all(data[x] for x in ('bear', 'horse', 'zebra'))))
        print(', '.join(output))
        return data

    def finalize(self):
        print(self.other_counter)


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
