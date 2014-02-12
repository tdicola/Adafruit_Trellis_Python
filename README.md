Adafruit Trellis Library For Python
===================================

This is a direct port of the [Adafruit Trellis library](https://github.com/adafruit/Adafruit_Trellis_Library) to Python and
intended to run on the Beaglebone Black, Raspberry Pi, or other embedded system with Python and I2C support.

<a href="http://imgur.com/qHF6tXM" title="Mobile Upload"><img src="http://i.imgur.com/qHF6tXMl.jpg" title="Hosted by imgur.com" alt="Mobile Upload"/></a>

Dependencies
------------

This library requires the Adafruit_I2C library is available.  You can install this library by following:

* On the Beaglebone Black, install the Adafruit_BBIO python package by [following this guide](http://learn.adafruit.com/setting-up-io-python-library-on-beaglebone-black/overview).

* On the Raspberry Pi, download the [Adafruit Raspberry Pi Python code](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code) and
copy the Adafruit_I2C.py file to the directory of your Trellis project.

Installation
------------

To install, download this repository and execute setup.py as root:

    sudo python setup.py install

Usage
-----

The functionality of the library is almost exactly the same as the standard Trellis library.  The important differences are:

* The Adafruit_Trellis class begin() method takes both an I2C address and I2C bus number.  This is to support devices with
multiple I2C buses.
  
  *  To find the I2C buses and pins for your hardware, check out [I2C on the Beaglebone Black](http://learn.adafruit.com/setting-up-io-python-library-on-beaglebone-black/i2c) or [I2C on the Raspberry Pi](http://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c).

* The Adafruit_TrellisSet class can use an arbitrary number of Trellises instead of being limited to 8.  With a device that has
more than one I2C bus (like the Beaglebone Black), you can control more than 8 Trellises!  Note that each I2C bus is still limited
to only 8 Trellis devices.

See examples of the library usage in the examples folder.  Note that you probably need to run scripts as root so they can access the I2C bus.  For example to run the TrellisTest example execute:

    sudo python TrellisTest.py

Changes
-------

* v1.0

  * Initial release
