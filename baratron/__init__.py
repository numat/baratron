#!/usr/bin/python
"""
Python driver for MKS eBaratron capacitance manometers, using ToolWeb.

Distributed under the GNU General Public License v2
Copyright (C) 2015 NuMat Technologies
"""
import xml.etree.ElementTree as ET

from tornado.httpclient import HTTPRequest, HTTPClient, AsyncHTTPClient


class CapacitanceManometer(object):
    """Python driver for MKS eBaratron capacitance manometers.

    More information on the device can be found [here]
    (http://www.mksinst.com/product/category.aspx?CategoryID=72).

    This class uses a tornado event loop to asynchronously retrieve data from
    the device. This can be used as an independent loop, registered with a
    larger loop, or simply ignored and used synchronously.
    """
    evids = {'pressure': 'EVID_100',
             'analog pressure': 'EVID_101',
             'run hours': 'EVID_102',
             'digital pressure, fraction of full scale': 'EVID_103',
             'analog pressure, fraction of full scale': 'EVID_104',
             'pressure units': 'EVID_105',
             'led color': 'EVID_106',
             'wait hours': 'EVID_107',
             'fw update (factory reserved)': 'EVID_110',
             'fw sec (factory reserved)': 'EVID_111',
             'refresh rate (website)': 'EVID_112',
             'offset (non-functional)': 'EVID_113',
             'drift': 'EVID_114',
             'zero (non-functional)': 'EVID_115',
             'disp res (website)': 'EVID_116',
             'plot data (website)': 'EVID_117',
             'rtp data (factory reserved)': 'EVID_118',
             'time (factory reserved)': 'EVID_198',
             'reset service (factory reserved)': 'EVID_199',
             'system status': 'EVID_208',
             'full-scale pressure': 'EVID_1103'}
    pressure_units = ['full-scale ratio', 'psi', 'torr', 'mtorr', 'cmH2O',
                      'inHg', 'inH2O', 'bar', 'mbar', 'Pa', 'kPa', 'atm',
                      'g / cm2']
    led = ['red', 'green', 'yellow', None, 'blinking']
    status = [None,
              'Signal Error (ADC0)',
              'Signal Error (ADC1)',
              'Calibration Checksum1 Failure',
              'Calibration Checksum2 Failure',
              'e-Baratron Outside Zeroing Range',
              'Zero Adjusted',
              None, None, None, None,
              'Diaphragm Shorted',
              'e-Baratron Over 110% of FS',
              None, None, None,
              'Pressure Over Set Limit',
              'Pressure Under Set Limit',
              None, None, None,
              'Illegal Access',
              None, None, None, None,
              'Power Supply Out of Spec',
              'e-Baratron Zeroing Recommended',
              'Cumulative Adjustment Over 20%',
              'Heater Failure']

    def __init__(self, address='192.168.1.100'):
        """Saves IP address and checks for live connection.

        Args:
            address: The IP address of the device, as a string.
                Default '192.168.1.100'.
        """
        self.address = 'http://{}/ToolWeb/Cmd'.format(address)

        # There's no documented method to change requested data, but it can be
        # done with e.g. `capacitance_manometer.fields.append('drift')`.
        self.fields = ['pressure', 'run hours', 'pressure units',
                       'led color', 'wait hours', 'system status',
                       'full-scale pressure']
        self.clients = {"sync": HTTPClient(), "async": AsyncHTTPClient()}

    def get(self, callback=None):
        """Retrieves the current state of the device through ToolWeb.

        Args:
            callback (Optional): If specified, this function will be triggered
                asyncronously on response.
        Returns:
            If a callback is not specified, this synchronously returns the
            state as a dictionary.
        """
        ids = ('<V Name="{}"/>'.format(self.evids[f]) for f in self.fields)
        body = '<PollRequest>{}</PollRequest>'.format(''.join(ids))
        request = HTTPRequest(self.address, 'POST', body=body)
        if callback:
            self.clients['async'].fetch(request,
                                        lambda r: callback(self._process(r)))
        else:
            return self._process(self.clients['sync'].fetch(request))

    def _process(self, response):
        """Converts XML sensor response string into a simplified dictionary."""
        if response.error:
            raise IOError(response.error)

        state = {}
        tree = ET.fromstring(response.body)
        for item in tree.findall('V'):
            evid, value = item.get("Name"), item.text
            key = next(k for k, v in self.evids.items() if v == evid)
            if key == 'pressure units':
                state[key] = self.pressure_units[int(value)]
            elif key == 'system status':
                i = int(value)
                statuses = ([s for bit, s in enumerate(self.status)
                             if s and bool(i >> bit & 1)] or ["ok"])
                state[key] = ', '.join(statuses)
            elif key == 'led color':
                i = int(value)
                led_statuses = ([s for bit, s in enumerate(self.led)
                                 if s and bool(i >> bit & 1)] or ["unknown"])
                state[key] = ', '.join(led_statuses)
            elif 'pressure' in key:
                state[key] = float(value)
            elif key in ['run hours', 'wait hours']:
                state[key] = float(value) / 3600.0
            else:
                state[key] = value
        return state


def command_line():
    import argparse
    import json
    from time import time

    parser = argparse.ArgumentParser(description="Read an MKS eBaratron "
                                     "capacitance manometer from the command "
                                     "line.")
    parser.add_argument('address', nargs='?', default='192.168.1.100',
                        help="The IP address of the eBaratron. Default "
                             "'192.168.1.100'.")
    parser.add_argument('--stream', '-s', action='store_true',
                        help="Sends a constant stream of sensor data, "
                             "formatted as a space-separated table.")
    args = parser.parse_args()

    manometer = CapacitanceManometer(args.address)

    if args.stream:
        try:
            headers = ["time", "pressure", "units", "max pressure",
                       "state", "LED color", "run (hours)", "wait (hours)"]
            print(''.join('{:<15}'.format(h) for h in headers))
            t0 = time()
            while True:
                d = manometer.get()
                print(("{time:<14.2f} {pressure:<14.1f} {pressure units:<14} "
                       "{full-scale pressure:<14.0f} {system status:<14} "
                       "{led color:<14} {run hours:<14.2f} {wait hours:<14.2f}"
                       ).format(time=time()-t0, **d))
        except KeyboardInterrupt:
            pass
    else:
        print(json.dumps(manometer.get(), indent=2, sort_keys=True))


if __name__ == "__main__":
    command_line()
