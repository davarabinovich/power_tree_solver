
from __future__ import annotations
from collections import namedtuple

IS_DEBUGGING = True
EPSILON = 0.0000001

LastHrids = namedtuple('LastHrids', 'power_inputs converters consumers')
