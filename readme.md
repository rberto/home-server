Logger
=====

Usage
-----

`python temp_pressure_logging -i 30 -p 540`

Will average inside temp and pressure read every 30s over 540s.
Will log the interior and exterior temp and pressure in a predifined db


Install
-------
Install pyowm a wrapper around the OpenWeatherMap service.
pip-3.2 install pyowm

smbus for using the i2c interface.
Today the smbus does not exist officaily for python3
here is a work around:

`
sudo apt-get install python-smbus libi2c-dev
wget http://ftp.de.debian.org/debian/pool/main/i/i2c-tools/i2c-tools_3.1.0.orig.tar.bz2     # download i2c-tools source
tar xf i2c-tools_3.1.0.orig.tar.bz2
cd i2c-tools-3.1.0/py-smbus
mv smbusmodule.c smbusmodule.c.orig  # backup
wget https://gist.githubusercontent.com/sebastianludwig/c648a9e06c0dc2264fbd/raw/2b74f9e72bbdffe298ce02214be8ea1c20aa290f/smbusmodule.c     # download patched (Python 3) source

python setup.py build
python setup.py install`


Web Interface and API
=====================

Usage
-----

`python web_interface.py`


Install
-------

tornado:

pip-3.2 install tornado
pip-3.2 install requests
pip-3.2 install python-nmap
