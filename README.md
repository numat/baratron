# baratron

Python driver and command line tool for ToolWeb-enabled [MKS eBaratron capacitance manometers](http://www.mksinst.com/product/category.aspx?CategoryID=72).

<p align="center">
  <img src="http://www.mksinst.com/images/pdimages/627c.jpg" />
</p>

Installation
============

```
pip install baratron
```

If you don't like pip, you can also install from source:

```
git clone https://github.com/numat/baratron.git
cd baratron
python setup.py install
```

Usage
=====

###Command Line

To test your connection and stream real-time data, use the command-line
interface. You can read the state with

```
$ baratron 192.168.1.100
{
  "full-scale pressure": 1000.0,
  "led color": "green",
  "pressure": 746.07721,
  "pressure units": "torr",
  "run hours": 29.66111111111111,
  "system status": "ok",
  "wait hours": 0.0
}
```

or stream a table of data with the `--stream` flag. See `baratron --help`
for more.

###Python

For more complex behavior, use the python interface.

```python
from baratron import CapacitanceManometer
cm = CapacitanceManometer("192.168.1.100")
print(cm.get())
```

If the device is operating at that IP address, this should return an output
a dictionary of the form:

```python
{
  "full-scale pressure": 1000.0, # Maximum pressure
  "led color": "green",          # Can be green, yellow, red, and blinking
  "pressure": 746.08,            # Current (digital) pressure
  "pressure units": "torr",      # Units of pressures
  "run hours": 29.66,            # Hours since powered on
  "system status": "ok",         # If not ok, displays error message
  "wait hours": 0.0              # If non-zero, the system is heating up
}
```

These are the default returned fields. The device can return a few additional
fields, but they are disabled by default (they're generally redundant).

Asynchronous
============

The above example works for small numbers of sensors. At larger scales,
the time spent waiting for sensor responses is prohibitive. Asynchronous
programming allows us to send out all of our requests in parallel, and then
handle responses as they trickle in. For more information, read through
[krondo's twisted introduction](http://krondo.com/?page_id=1327).

```python
from baratron import CapacitanceManometer
from tornado.ioloop import IOLoop, PeriodicCallback


def on_response(response):
    """This function gets run whenever the device responds."""
    print(response)


def loop():
    """This function will be called in an infinite loop by tornado."""
    cm.get(on_response)


cm = CapacitanceManometer()
PeriodicCallback(loop, 500).start()
IOLoop.current().start()
```

This looks more complex, but the advantages are well worth it at scale.
Essentially, sleeping is replaced by scheduling functions with tornado. This
allows your code to do other things while waiting for responses.
