Welcome to iBeam Smart Laser's documentation!
=============================================

iBeam Smart Laser controller usage example
------------------------------------------

First, run the iBeam Smart Laser controller::

    $ aqctl_artiq_ibeam_smart -d device

.. note::
    Device is tty device. Most likely in the from '/dev/ttyUSB0' 


Then, send commands to it via the ``sipyco_rpctool`` utility::

    $ sipyco_rpctool 127.0.0.1 3281 call set_channel_on 1 1
    $ sipyco_rpctool 127.0.0.1 3281 call set_channel_power 2 2000

API
---

.. automodule:: artiq_ibeam_smart.driver
    :members:


ARTIQ Controller
----------------

.. argparse::
   :ref: artiq_ibeam_smart.aqctl_artiq_ibeam_smart.get_argparser
   :prog: aqctl_artiq_ibeam_smart


.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`




