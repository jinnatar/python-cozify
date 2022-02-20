python-cozify
=============

|docs| |ci| |coverage| |pyversions| |gitter|

Unofficial Python3 API bindings for the (unpublished) Cozify API.
Includes high-level helpers for easier use of the APIs,
for example an automatic authentication flow, and low-level 1:1 API functions.

.. contents:: :local:

Installation
------------

Python3.8 is the current minimum supported version of Python.
For example Ubuntu 20.04 LTS is still supported out of the box, older versions may need a manual Python upgrade or PPA.

The recommended way is to install from PyPi:

.. code:: console

       sudo -H pip3 install cozify

To benefit from new features you'll need to update the library (pip does not auto-update):

.. code:: console

       sudo -H pip3 install -U cozify

or if developing, clone the main branch of this repo (main stays at current release) and:

.. code:: console

       curl -sSL https://install.python-poetry.org | python -
       poetry install

To develop python-cozify clone the devel branch and submit pull requests against the devel branch.
New releases are cut from the devel branch as needed.

Basic usage
-----------
These are merely some simple examples, for the full documentation see: `http://python-cozify.readthedocs.io/en/latest/`

read devices by capability, print temperature data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from cozify import hub
    devices = hub.devices(capabilities=hub.capability.TEMPERATURE)
    for id, dev in devices.items():
      print('{0}: {1}C'.format(dev['name'], dev['state']['temperature']))

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

On Capabilities
---------------
The most practical way to "find" devices for operating on is currently to filter the devices list by their capabilties. The
most up to date list of recognized capabilities can be seen at `cozify/hub.py <cozify/hub.py#L21>`_

If the capability you need is not yet supported, open a bug to get it added. One way to compare your live hub device's capabilities
to those implemented is running the util/capabilities_list.py tool. It will list implemented and gathered capabilities from your live environment.
To get all of your previously unknown capabilities implemented, just copy-paste the full output of the utility into a new bug.

In short capabilities are tags assigned to devices by Cozify that mostly guarantee the data related to that capability will be in the same format and structure.
For example the capabilities based example code in this document filters all the devices that claim to support temperature and reads their name and temperature state.
Multiple capabilities can be given in a filter by providing a list of capabilities. By default any capability in the list can match (OR filter) but it can be flipped to AND mode
where every capability must be present on a device for it to qualify. For example, if you only want multi-sensors that support both temperature and humidity monitoring you could define a filter as:

.. code:: python

    devices = hub.devices(capabilities=[ hub.capability.TEMPERATURE, hub.capability.HUMIDITY ], and_filter=True)

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

Working Remotely
----------------
By default queries to the hub are attempted via local LAN. Also by default "remoteness" autodetection is on and thus
if it is determined during cloud.authentication() or a hub.ping() call that you seem to not be in the same network, the state is flipped.
Both the remote state and autodetection can be overriden in most if not all funcions by the boolean keyword arguments 'remote' and 'autoremote'. They can also be queried or permanently changed by the hub.remote() and hub.autoremote() functions.

Using Multiple Hubs
-------------------
Everything has been designed to support multiple hubs registered to the same Cozify Cloud account. All hub operations can be targeted by setting the keyword argument 'hub_id' or 'hub_name'. The developers do not as of yet have access to multiple hubs so proper testing of multi functionality has not been performed. If you run into trouble, please open bugs so things can be improved.

The remote state of hubs is kept separately so there should be no issues calling your home hub locally but operating on a summer cottage hub remotely at the same time.

Enconding Pitfalls
------------------
The hub provides data encoded as a utf-8 json string. Python-cozify transforms this into a Python dictionary
where string values are kept as unicode strings. Normally this isn't an issue, as long as your system supports utf-8.
If not, you will run into trouble printing for example device names with non-ascii characters:

    UnicodeEncodeError: 'ascii' codec can't encode character '\xe4' in position 34: ordinal not in range(128)

The solution is to change your system locale to support utf-8. How this is done is however system dependant.
As a first test try temporarily overriding your locale:

.. code:: console

    LC_ALL='en_US.utf8' python3 program.py

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
pytest is used for unit tests.

-  Certain tests are marked as "live" tests and require an active authentication state and a real hub to query against. Live tests are non-destructive.
-  Some tests are marked as "destructive" and will cause changes such as a light being turned on or tokens getting invalidated on purpose.
-  A few tests are marked as "remote" and are only expected to succeed when testing remotely, i.e. outside the LAN of the hub.
-  A few tests are marked as "mbtest" and will only work if a MonteBank server is available. If a non-local instance is desired, provide a .env file with MBTEST_HOST set.
-  Most tests are marked as "logic" and do not require anything external. If no set is defined, only logic tests are run.

During development you can run the test suite right from the source directory:

.. code:: console

    pytest
    # or run only live tests:
    pytest -m live
    # run everything except destructive * MonteBank tests:
    pytest -m "not destructive and not mbtest"

To run the test suite on an already installed python-cozify (defining a set is mandatory, otherwise ALL sets are run including destructive):

.. code:: console

    pytest -v -m logic --pyargs cozify


Roadmap, aka. Current Limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Authentication flow has been improved quite a bit but it would benefit a lot from real-world feedback.
-  For now there are only read calls. Next up is implementing ~all hub calls at the raw level and then wrapping them for ease of use. If there's something you want to use sooner than later file an issue so it can get prioritized!
-  Device model is non-existant and the old implementations are bad and deprecated. Active work ongoing to filter by capability at a low level first, then perhaps a more object oriented model on top of that.


.. |docs| image:: https://readthedocs.org/projects/python-cozify/badge/?version=latest
  :target: http://python-cozify.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. |ci| image:: https://travis-ci.com/Artanicus/python-cozify.svg?branch=main
  :target: https://travis-ci.com/Artanicus/python-cozify
  :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/Artanicus/python-cozify/branch/main/graph/badge.svg
  :target: https://codecov.io/gh/Artanicus/python-cozify
  :alt: Coverage Status


.. |pyversions| image:: https://img.shields.io/pypi/pyversions/cozify.svg
  :alt: PyPI - Python Version

.. |gitter| image:: https://badges.gitter.im/python-cozify/Lobby.svg
  :alt: Join the chat at https://gitter.im/python-cozify/Lobby
  :target: https://gitter.im/python-cozify/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
