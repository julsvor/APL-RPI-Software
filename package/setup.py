from setuptools import setup, find_packages


setup(
    name="tvi_lib",
    version="1.0",
    author="Julius Svoren",
    author_email="julsvor@gmail.com",
    description="An internal library used for processing signals, resolving numbers and network calling server/client",
    url="https://github.com/julsvor/APL-RPI-Software",
    packages=['tvi_lib'],
    scripts=[
            'bin/tvi-dbcli.py',
            'bin/tvi-manager-gui.py',
            'bin/tvi-run.py',
    ],
    install_requires=[
        'mariadb'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
