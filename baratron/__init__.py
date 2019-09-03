"""
Python driver for MKS eBaratron capacitance manometers.

Distributed under the GNU General Public License v2
Copyright (C) 2019 NuMat Technologies
"""
from baratron.driver import CapacitanceManometer


def command_line():
    """Command-line tool for MKS eBaratron capacitance manometers."""
    import argparse
    import asyncio
    import json
    import sys
    red, reset = '\033[1;31m', '\033[0m'

    parser = argparse.ArgumentParser(description="Read an MKS eBaratron "
                                     "capacitance manometer from the command "
                                     "line.")
    parser.add_argument('address', nargs='?', default='192.168.1.100',
                        help="The IP address of the eBaratron. Default "
                             "'192.168.1.100'.")
    args = parser.parse_args()

    async def get():
        try:
            async with CapacitanceManometer(args.address) as manometer:
                print(json.dumps(await manometer.get(), indent=4, sort_keys=True))
        except asyncio.TimeoutError:
            sys.stderr.write(f'{red}Could not connect to device.{reset}\n')
        except Exception as e:
            sys.stderr.write(f'{red}{e}{reset}\n')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get())
    loop.close()


if __name__ == '__main__':
    command_line()
