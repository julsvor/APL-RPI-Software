from setuptools import setup, find_packages
import subprocess


setup(
    name="tvi_lib",
    version="1.0",
    author="Julius Svoren",
    author_email="julsvor@gmail.com",
    description="An internal library used for processing signals, resolving numbers and network calling server/client",
    url="https://github.com/julsvor/APL-RPI-Software",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tvi-run=tvi_lib.run:main',
            'tvi-dbcli=tvi_lib.dbcli:main',
            'tvi-manager-gui=tvi_lib.manager_gui:main',
            ],
        },
    install_requires=[
        'gpiozero',
    ]
)

