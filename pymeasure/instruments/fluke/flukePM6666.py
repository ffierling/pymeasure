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

class FlukePM6666(Instrument):
    """ Represents a simplified Fluke PM6666 Frequency Counter and
    provides a high-level interface for interacting with the instrument.

    This simple model of a counter uses Agilent nomenclature to minimize
    the changes necessary to swap a different counter into the test
    environment.  Manufacturer and model specific commands not supported
    by most counters should be implemented with read, write and ask
    methods.
    """

    FUNCTIONS = {'FREQ': 'FREQ',
                  'PER': 'PER',
                 'TINT': 'TIME',
                 'TOT' : 'TOTM'
    }

    GATES = ('TIME',)

    INPUTS = ('ATT', 'COUP', 'IMP'
    )

    error = Instrument.measurement(
        "SYST:ERR?", 
        """ Returns oldest error as a list comprising [<error number>, <error string>] """
    )

    def __init__(self, resourceName, **kwargs):
        super(FlukePM6666, self).__init__(
            resourceName,
            "Fluke PM6666 Frequency Counter",
            **kwargs
        )
        #self.rw_delay = 0.1 #  Don't use because it applies to every instrument on the adapter
        self.reset()

    def reset(self):
        """ Reset counter to a known state """
        self.write("D")  # Device clear, returns to default settings
        self.write("EOI ON")
        self.func = 'FREQ'

    def function(self, cmd):
        f = cmd.split()
        
        if f[0] in self.FUNCTIONS:
            self.func = f[0]
            self.write("FUNC '%s'" % cmd)
        else:
            return  # ??? error processing

    def measure(self):
        self.write('INIT')  # Initiate measurement
        x = self.ask('*OPC?')  # Put 1 in buffer when done
        #i = 0
        while x == '':
            x = self.read()
            #i += 1
        #print(i)
        #print(x.encode('utf-8').hex())
        return float(self.ask('FETC:%s?' % self.func))

    def gate(self, cmd):
        f = cmd.split()

        if f[0] == 'TIME':
            self.write(":FREQ:ARM:STAR:SOUR IMM")
            self.write(":FREQ:ARM:STOP:SOUR TIM")
            self.write(":FREQ:ARM:STOP:TIM  %f" % float(f[1]))
        elif f[0] == 'DIGITS':
            self.write(":FREQ:ARM:STAR:SOUR IMM")
            self.write(":FREQ:ARM:STOP:SOUR TIM")
            self.write(":FREQ:ARM:STOP:DIG  %f" % float(f[1]))
        else:
            return  # ??? error processing

    def input(self, cmd, n=1):
        f = cmd.split()

        if f[0] == 'ATT':
            self.write(":INP%d:ATT  %d" % (n, int(f[1])))

        elif f[0] == 'COUP':
            self.write(":INP%d:COUP  %s" % (n, f[1]))

        elif f[0] == 'IMP':
            self.write(":INP%d:IMP  %f" % (n, float(f[1])))

        else:
            return  # ??? error processing
