python-cozify
=============

Unofficial Python3 API bindings for the (unpublished) Cozify API.
Includes high-level helpers for easier use of the APIs,
for example an automatic authentication flow, and low-level 1:1 API functions.

Installation
------------

The recommended way is to install from PyPi:

.. code:: bash

       sudo -H pip3 install cozify

or clone the master branch of this repo (master stays at current release) and:

.. code:: bash

       sudo python3 setup.py install

To develop python-cozify clone the devel branch and submit pull requests against the devel branch.
New releases are cut from the devel branch as needed.

Basic usage
-----------
These are merely some simple examples, for the full documentation see: `http://python-cozify.readthedocs.io/en/latest/`

read devices, extract multisensor data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from cozify import hub, multisensor
    devices = hub.getDevices()
    print(multisensor.getMultisensorData(devices))

only authenticate
~~~~~~~~~~~~~~~~~

.. code:: python

    from cozify import cloud
    cloud.authenticate()
    # authenticate() is interactive and usually triggered automatically
    # authentication data is stored in ~/.config/python-cozify/python-cozify.cfg

authenticate with a non-default state storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from cozify import cloud, config
    config.setStatePath('/tmp/testing-state.cfg')
    cloud.authenticate()
    # authentication and other useful data is now stored in the defined location instead of ~/.config/python-cozify/python-cozify.cfg
    # you could also use the environment variable XDG_CONFIG_HOME to override where config files are stored

Keeping authentication valid
----------------------------
If the cloud token expires, the only option to get a new one is an interactive prompt for an OTP.
Since most applications will want to avoid that as much as possible there are a few tips to keep a valid token alive.
At the time of writing tokens are valid for 28 days during which they can be seamlessly refreshed.

In most cases it isn't necessary to directly call cloud.refresh() if you're already using cloud.ping() to test token validity.
cloud.ping() will also perform a refresh check after a successful ping unless explicitly told not to do so.

To refresh a token you can call as often as you want:

.. code:: python

    cloud.refresh()

By default keys older than a day will be re-requested and otherwise no refresh is performed. The refresh can be forced:

.. code:: python

    cloud.refresh(force=True)

And the expiry duration can be altered (also when calling cloud.ping()):

.. code:: python

    cloud.refresh(expiry=datetime.timedelta(days=20))
    # or
    cloud.ping(autorefresh=True, expiry=datetime.timedelta(days=20))

Sample projects
---------------

-  `github.com/Artanicus/cozify-temp <https://github.com/Artanicus/cozify-temp>`__
   - Store Multisensor data into InfluxDB
-  Take a look at the util/ directory for some crude small tools using the library that have been useful during development.
-  File an issue to get your project added here

Development
-----------
To develop python-cozify clone the devel branch and submit pull requests against the devel branch.
New releases are cut from the devel branch as needed.
    
Tests
~~~~~
pytest is used for unit tests. Test coverage is still quite spotty and under active development.
Certain tests are marked as "live" tests and require an active authentication state and a real hub to query against.
Live tests are non-destructive.

During development you can run the test suite right from the source directory:

.. code:: bash

    pytest -v cozify/
    # or include the live tests as well:
    pytest -v cozify/ --live

To run the test suite on an already installed python-cozify:

.. code:: bash

    pytest -v --pyargs cozify
    # or including live tests:
    pytest -v --pyargs cozify --live


Roadmap, aka. Current Limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Authentication flow has been improved quite a bit but it would benefit a lot from real-world feedback.
-  For now there are only read calls. Next up is implementing ~all hub calls at the raw level and then wrapping them for ease of use. If there's something you want to use sooner than later file an issue so it can get prioritized!
-  Device model is non-existant and the old implementations are bad and deprecated. Active work ongoing to filter by capability at a low level first, then perhaps a more object oriented model on top of that.
