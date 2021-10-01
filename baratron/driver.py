"""
Python driver for MKS eBaratron capacitance manometers.

Distributed under the GNU General Public License v2
Copyright (C) 2019 NuMat Technologies
"""
from xml.etree import ElementTree

import aiohttp


class CapacitanceManometer(object):
    """Driver for MKS eBaratron capacitance manometers.

    More information on the device can be found [here]
    (http://www.mksinst.com/product/category.aspx?CategoryID=72).
    """

    evids = {
        'pressure': 'EVID_100',
        'run hours': 'EVID_102',
        'pressure units': 'EVID_105',
        'led color': 'EVID_106',
        'wait hours': 'EVID_107',
        'drift': 'EVID_114',
        'system status': 'EVID_208',
        'full-scale pressure': 'EVID_1103'
    }
    pressure_units = [
        'full-scale ratio',
        'psi',
        'torr',
        'mtorr',
        'cmH2O',
        'inHg',
        'inH2O',
        'bar',
        'mbar',
        'Pa',
        'kPa',
        'atm',
        'g / cm2'
    ]
    led = [
        'red',
        'green',
        'yellow',
        None,
        'blinking'
    ]
    status = [
        None,
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
        'Heater Failure'
    ]

    def __init__(self, address: str, timeout: float = 1.0):
        """Initialize device.

        Note that this constructor does not not connect. This will happen
        on the first avaiable async call (ie. `await manometer.get()` or
        `async with CapacitanceManometer(ip) as manometer`).

        Args:
            address: The IP address of the device, as a string.
            timeout (optional): Time to wait for a response before throwing
                a TimeoutError. Default 1s.
        """
        self.address = f"http://{address.lstrip('http://').rstrip('/')}/ToolWeb/Cmd"
        self.session = None
        self.Timeout = aiohttp.ClientTimeout(total=timeout)
        ids = ''.join(f'<V Name="{evid}"/>' for evid in self.evids.values())
        body = f'<PollRequest>{ids}</PollRequest>'
        self.request = {
            'headers': {'Content-Type': 'text/xml'},
            'data': body
        }

    async def __aenter__(self):
        """Support `async with` by entering a client session."""
        await self.connect()
        return self

    async def __aexit__(self, *err):
        """Support `async with` by exiting a client session."""
        await self.disconnect()

    async def connect(self):
        """Connect with device, opening persistent session."""
        self.session = aiohttp.ClientSession(timeout=self.Timeout)

    async def disconnect(self):
        """Close the underlying session, if it exists."""
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def get(self):
        """Retrieve the current state of the device."""
        return self._process(await self._request())

    def _process(self, response):
        """Convert XML response into a simplified dictionary."""
        state = {}
        tree = ElementTree.fromstring(response)
        for item in tree.findall('V'):
            evid, value = item.get('Name'), item.text
            key = next(k for k, v in self.evids.items() if v == evid)
            if key == 'pressure units':
                state[key] = self.pressure_units[int(value)]
            elif key == 'system status':
                i = int(value)
                statuses = ([s for bit, s in enumerate(self.status)
                             if s and bool(i >> bit & 1)] or ['ok'])
                state[key] = ', '.join(statuses)
            elif key == 'led color':
                i = int(value)
                led_statuses = ([s for bit, s in enumerate(self.led)
                                 if s and bool(i >> bit & 1)] or ['unknown'])
                state[key] = ', '.join(led_statuses)
            elif key in ['pressure', 'full-scale pressure', 'drift']:
                state[key] = float(value)
            elif key in ['run hours', 'wait hours']:
                state[key] = float(value) / 3600.0
            else:
                state[key] = value
        return state

    async def _request(self):
        """Handle sending an HTTP request.

        This reads through "ToolWeb", which seems like SOAP with some extra
        terminology. Upside is that SOAP is well supported.
        """
        if self.session is None:
            await self.connect()
        async with self.session.post(self.address, **self.request) as r:
            response = await r.text()
            if not response or r.status > 200:
                raise IOError(
                    f"Could not communicate with eBaratron at '{self.address}'."
                )
            return response
