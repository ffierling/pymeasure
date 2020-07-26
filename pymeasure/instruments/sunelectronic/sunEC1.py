#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set

class SunEC1(Instrument):
    ''' Represents the Sun Electronic EC1 Environment Chamber
    and provides a high-level interface for interacting
    with the instrument
    '''
    # SUN EC1A Range: -73 to 315 C
    C_TEMPS = range(-1, 72)  # Commercial temperature range -0 to 70 C +/- 1
    I_TEMPS = range(-41, 87)  # Industrial temperature range -40 to 85 C +/- 1
    M_TEMPS = range(-56, 127)  # Military temperature range -55 to 125 C +/- 1
    D_TEMPS = range(30, 36)  # Debug temperature range
    TEMPS = D_TEMPS

    DEFAULT_DWELL = 60  # Seconds to dwell at set temperature
    TEMP_TOL_INIT = 0.5  # Start run when user probe within this temperature
    TEMP_TOL = 0.5  # Warn if chamber outside this limit
    TEMP_RATE_INIT = 20  # ramping rate during initialization in degrees Celcius / minute (max: 30)
    TEMP_RATE_MEASURE = 10  # ramping rate during measurement in degrees Celcius / minute
    TEMP_RATE_MARGIN = 25  # percentage of ramp_time to wait for slow thermal response

    MODEs = ('HEAT', 'COOL')

    def __init__(self, resourceName, **kwargs):
        super(SunEC1, self).__init__(
            resourceName,
            "Sun Electronic EC1 Environment Chamber",
            **kwargs
        )

        self. write('ON') # Only command it responds to after power-up

    def id(self):
        '''Override method in base class that uses SCPI command'''

        self.ask('VER?')

    def mode(self, m, rate=TEMP_RATE_INIT):
        '''Set mode, 'HEAT', 'COOL' or both'''

        for i in split(m):
            if i == 'HEAT':
                self.write('HON')
            elif i == 'COOL':
                self.write('CON')

        self.write('RATE=%d' % (rate))
