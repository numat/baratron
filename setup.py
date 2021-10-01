"""Python driver and command line tool for MKS eBaratron manometers."""
from setuptools import setup

with open('README.md', 'r') as in_file:
    long_description = in_file.read()

setup(
    name='baratron',
    version='0.3.1',
    description='Python driver for MKS eBaratron capacitance manometers.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://github.com/numat/baratron/',
    author='Patrick Fuller',
    author_email='pat@numat-tech.com',
    packages=['baratron'],
    install_requires=['aiohttp>=3.3'],
    entry_points={
        'console_scripts': [('baratron = baratron:command_line')]
    },
    license='GPLv2',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces'
    ]
)
