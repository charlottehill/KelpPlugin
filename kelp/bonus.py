"""This plugin is for the Predator Prey Project &  Sequence Lesson."""

from __future__ import print_function
from collections import Counter
from kelpplugin import KelpPlugin
import os
import sys
import kurt
import PIL

class Bonus(KelpPlugin):
    def __init__(self):
        super(Bonus, self).__init__

    def analyze(self, scratch):
        if not getattr(scratch, 'kelp_prepared', False):
            KelpPlugin.tag_reachable_scripts(scratch)
        return {}


def bonus_display(seq):
    html = []
    html.append('<h2 style="background-color:LightGreen">')
    html.append('Great job completing this bonus project!')
    html.append('</h2>')
    return ''.join(html)
