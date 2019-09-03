baratron
========

Python driver and command line tool for ToolWeb-enabled [MKS eBaratron capacitance manometers](http://www.mksinst.com/product/category.aspx?CategoryID=72).

<p align="center">
  <img src="http://premier-sols.com/images/stories/Lesker/Pressure-Measurement/MKS%20628C%20e-Series%20Capacitance%20Manometers.jpg" height="300">
</p>

Installation
============

```
pip install baratron
```

If you want to use the older python2/tornado implementation, use `pip install baratron==0.1.2`.

Usage
=====

### Command Line

To test your connection and stream real-time data, use the command-line
interface. You can read the device with:

```
$ baratron 192.168.1.100
{
    "drift": 0.00164,
    "full-scale pressure": 1000.0,
    "led color": "green",
    "pressure": 3.78864,
    "pressure units": "torr",
    "run hours": 17517.763055555555,
    "system status": "e-Baratron Zeroing Recommended",
    "wait hours": 0.0
}
```

### Python

This uses Python ≥3.5's async/await syntax to asynchronously communicate with
the device. For example:

```python
import asyncio
import baratron

async def get():
    async with baratron.CapacitanceManometer('the-baratron-ip-address') as sensor:
        print(await sensor.get())

asyncio.run(get())
```
