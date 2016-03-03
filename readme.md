Logger
=====

Usage
-----

> python temp_pressure_logging -i 30 -p 540

Will average inside temp and pressure read every 30s over 540s.
Will log the interior and exterior temp and pressure in a predifined db


Install
-------

> pip-3.2 install pyowm



Web Interface and API
=====================

Usage
-----

> python web_interface.py


Install
-------

# dependancies for tornado:
https://pypi.python.org/pypi/backports.ssl_match_hostname
and 
https://pypi.python.org/pypi/certifi
and 
sudo apt-get install build-essential python-dev

# dependancies for backport
setuptools
install command: wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
