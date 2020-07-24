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

class Agilent53132A(Instrument):
    """ Represents the Agilent 53132A Frequency Counter
    with a S/N prefix >= 3646 and provides a high-level
    interface for interacting with the instrument.
    """  # Tested on a 53132A with firmware revision 3944

    FUNCTIONS = ('DCYC', 'FTIM', 'FREQ', 'MAX',
            'MIN', 'NWID', 'PER', 'PHA', 'PTP',
            'PWID', 'RTIM', 'TINT', 'TOT'
    )

    function_ = Instrument.control(
        "FUNC?", "FUNC '%g'",
        """ A floating point property that controls the frequency of the
        output in Hz. The allowed range depends on the waveform shape
        and can be queried with :attr:`~.max_frequency` and 
        :attr:`~.min_frequency`. """
    )

    error = Instrument.measurement(
        "SYST:ERR?", 
        """ Returns oldest error as a list comprising [<error number>, <error string>] """
    )

    def __init__(self, resourceName, **kwargs):
        super(Agilent53132A, self).__init__(
            resourceName,
            "Agilent 53132A Frequency Counter",
            **kwargs
        )
        #self.rw_delay = 0.1 #  Don't use because it applies to every instrument on the adapter
        self.reset()

    def reset(self):
        """ Reset counter to a known state """
        self.write("*RST")
        self.write("*CLS")
        self.write("*SRE 0")
        self.write("*ESE 0")
        self.write(":STAT:PRES")
        self.func = 'FREQ'

    def function(self, cmd):
        f = cmd.split()
        
        if f[0] in FUNCTIONS:
            self.func = f[0]
            self.write("FUNC '%s'" % cmd)
        else:
            return  # ??? error processing

    def measure():
        self.write('INIT')  # Initiate measurement
        x = self.ask('*OPC?')  # Put 1 in buffer when done
        #i = 0
        while x == '':
            x = self.read()
            #i += 1
        #print(i)
        #print(x.encode('utf-8').hex())
        return float(self.ask('FETC:%s?' % self.func))

    def gate(time=10e-3):
        self.write(":FREQ:ARM:STAR:SOUR IMM")
        self.write(":FREQ:ARM:STOP:SOUR TIM")
        self.write(":FREQ:ARM:STOP:TIM  %f" % time)
