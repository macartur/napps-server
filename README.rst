|Tag| |Release| |Tests| |License|

############
Napps-Server
############

*napps-server* is an application repository to store and manage SDN
applications which runs on top of kytos controller. A command line is
provided with kytos to querie and install applications easily.

This web server is part of *Kytos* project and was developed to share,
find and reuse SDN applications. A REST API is provided to perform
queries and install applications.

For more information about, please visit our `Kytos web
site <http://kytos.io/>`__.

QuickStart
**********

Installing
==========

In order to install Napps-Server and create a SDN repository for your
application you must install `Redis
database <http://redis.io/topics/quickstart>`__, then install the napps-server
using the source code or via pip.

REDIS Installation
------------------

For installing Redis you can follow `Redis Quick
Start <http://redis.io/topics/quickstart>`__ guide for details. Also we
provide an small steps to install Redis and load the schema to be used for
testing the installation.The steps are:

First step is install the redis dependencies running the commands:

Ubuntu/Debian
^^^^^^^^^^^^^
.. code-block:: shell

  $ sudo apt-get update
  $ sudo apt-get install gcc wget make tar

Fedora
^^^^^^

.. code-block:: shell

  $ sudo dnf update
  $ sudo dnf install gcc wget make tar

Centos
^^^^^^

.. code-block:: shell

  $ sudo yum update
  $ sudo yum install gcc wget make tar


After that, we must install the Redis server running the commands:

.. code-block:: bash

  $ cd /tmp
  $ wget http://download.redis.io/redis-stable.tar.gz
  $ tar xvzf redis-stable.tar.gz
  $ cd redis-stable
  $ make
  $ sudo make install

Finally to load the schema we need run the redis command line passing the
schema_redis.nosql content.We can do this running the command:

.. code-block:: bash

  $  schema_redis.nosql ./redis-cli


Napps-Server Installation
-------------------------

*Kyco* is in PyPI repository, so you can easily install it via `pip3` (`pip`
for Python 3) or include this project in your `requirements.txt`.

Installing from PyPI
^^^^^^^^^^^^^^^^^^^^

After installed `pip3` you can install *napps-server* running:

.. code:: shell

    $ sudo pip3 install kyco


Installing from source code
^^^^^^^^^^^^^^^^^^^^^^^^^^^

First you need to clone *napps-server* repository:

.. code-block:: shell

   $ git clone https://github.com/kytos/napps-server.git

After cloning, the installation process is done by standard `setuptools`
install procedure:

.. code-block:: shell

   $ cd napps-server
   $ sudo python3 setup.py install


Main Highlights
***************

Speed focused
=============

We keep the word *performance* in mind since the beginning of the
development. Also, as computer scientists, we will always try to get the
best performance by using the most suitable algorithms.

Rest APIs
=========

This web server was developed to provide simple and powerfull Rest APIs.
By using this APIs you will be able to query, update, add and delete
your applications in this repository.

Born to be free
===============

OpenFlow was born with a simple idea: make your network more vendor
agnostic and we like that!

We are advocates and supporters of free software and we believe that the
more eyes observe the code, the better it will be. This project can
receive support from many vendors, but will never follow a particular
vendor direction.

*napps-server* will always be free software.

Authors
*******

For a complete list of authors, please open ``AUTHORS.md`` file.

Contributing
************

If you want to contribute to this project, please read
`CONTRIBUTE.md <CONTRIBUTE.md>`__ and `HACKING.md <HACKING.md>`__ files.

License
*******

This software is under *MIT-License*. For more information please read
``LICENSE`` file.

.. |Tag| image:: https://img.shields.io/github/tag/kytos/python-openflow.svg
   :target: https://github.com/kytos/python-openflow/tags
.. |Release| image:: https://img.shields.io/github/release/kytos/python-openvpn.svg
   :target: https://github.com/kytos/python-openflow/releases
.. |Tests| image:: https://api.travis-ci.org/kytos/napps-server.svg?branch=develop
   :target: https://travis-ci.org/kytos/napps-server
.. |License| image:: https://img.shields.io/github/license/kytos/python-openflow.svg
   :target: https://github.com/kytos/python-openflow/blob/master/LICENSE
