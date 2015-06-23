from setuptools import setup

setup(
    name="baratron",
    version="0.1.0",
    description="Python driver for MKS eBaratron capacitance manometers.",
    url="http://github.com/numat/baratron/",
    author="Patrick Fuller",
    author_email="pat@numat-tech.com",
    packages=["baratron"],
    install_requires=["tornado"],
    entry_points={
        "console_scripts": [("baratron = baratron:command_line")]
    },
    license="GPLv2",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces"
    ]
)
