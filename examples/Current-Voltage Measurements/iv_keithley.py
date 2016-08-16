"""
This example demonstrates how to make a graphical interface to preform
IV characteristic measurements. There are a two items that need to be 
changed for your system:

1) Correct the GPIB addresses in IVProcedure.startup for your instruments
2) Correct the directory to save files in MainWindow.queue

Run the program by changing to the directory containing this file and calling:

python iv_keithley.py

"""

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

import sys
from time import sleep
import numpy as np

from pymeasure.instruments.keithley import Keithley2000, Keithley2400
from pymeasure.instruments import Instrument
from pymeasure.log import console_log
from pymeasure.experiment import Results
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, FloatParameter
from pymeasure.experiment import unique_filename


class IVProcedure(Procedure):

    max_current = FloatParameter('Maximum Current', units='mA', default=10)
    min_current = FloatParameter('Minimum Current', units='mA', default=-10)
    current_step = FloatParameter('Current Step', units='mA', default=0.1)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    voltage_range = FloatParameter('Voltage Range', units='V', default=10)

    DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Resistance (Ohm)']

    def startup(self):
        log.info("Setting up instruments")
        self.meter = Keithley2000("GPIB::25")
        self.meter.mode = 'voltage'
        self.meter.voltage_range = self.voltage_range
        self.meter.voltage_nplc = 1 # Integration constant to Medium
        
        self.source = Keithley2400("GPIB::1")
        self.source.source_mode = 'current'
        self.source.source_current_range = self.max_current*1e-3 # A
        self.source.complinance_voltage = self.voltage_range
        self.source.enable_source()
        sleep(2)

    def execute(self):
        currents_up = np.arange(self.min_current, self.max_current, self.current_step)
        currents_down = np.arange(self.max_current, self.min_current, -self.current_step)
        currents = np.concatenate((currents_up, currents_down)) # Include the reverse
        currents *= 1e-3 # to mA from A
        steps = len(currents)
        
        log.info("Starting to sweep through current")
        for i, current in enumerate(currents):
            log.debug("Measuring current: %g mA" % current)
            self.source.source_current = current
            sleep(self.delay*1e-3)
            voltage = self.meter.voltage
            if abs(current) <= 1e-10:
                resistance = np.nan
            else:
                resistance = voltage/current
            data = {
                'Current (A)': current,
                'Voltage (V)': voltage,
                'Resistance (Ohm)': resistance
            }
            self.emit('results', data)
            self.emit('progress', 100.*i/steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.source.shutdown()
        log.info("Finished")


class MainWindow(ManagedWindow):

    def __init__(self):
        super(MainWindow, self).__init__(
            procedure_class=IVProcedure,
            inputs=[
                'max_current', 'min_current', 'current_step',
                'delay', 'voltage_range'
            ],
            displays=[
                'max_current', 'min_current', 'current_step',
                'delay', 'voltage_range'
            ],
            x_axis='Current (A)',
            y_axis='Voltage (V)'
        )
        self.setWindowTitle('IV Measurement')

    def queue(self):
        directory = "./" # Change this to the desired directory
        filename = unique_filename(directory, prefix='IV')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())