Napps-Server
============

|Tag| |Release| |Tests| |License|

*napps-server* is an application repository to store and manage SDN
applications which runs on top of kytos controller. A command line is
provided with kytos to querie and install applications easily.

This web server is part of *Kytos* project and was developed to share,
find and reuse SDN applications. A REST API is provided to perform
queries and install applications.

For more information about, please visit our `Kytos web
site <http://kytos.io/>`__.

Installing
----------

Dependences
~~~~~~~~~~~

In order to install Napps-Server and create a SDN repository for your
application you must install `REDIS
database <http://redis.io/topics/quickstart>`__

Naps-Server Installation
~~~~~~~~~~~~~~~~~~~~~~~~

You can install this package from source or via pip. If you have cloned
this repository and want to install it via ``setuptools``, please run:

.. code:: bash

    sudo python3 setup.py install

Or, to install via pip, please execute:

.. code:: bash

    sudo pip3 install napps-server

REDIs Installation
~~~~~~~~~~~~~~~~~~

For installing REDIs you can follow `Redis Quick
Start <http://redis.io/topics/quickstart>`__ guide for details. Also we
provide an small REDIs schema to be used for testing the installation.
To install the REDIs schema, run the command:

.. code:: bash

    cd to_REDIs_Installation_dir
    cd src/
    cat napps_server_git_repo_dir/schema_redis.nosql | ./redis-cli

Main Highlights
---------------

Speed focused
~~~~~~~~~~~~~

We keep the word *performance* in mind since the beginning of the
development. Also, as computer scientists, we will always try to get the
best performance by using the most suitable algorithms.

Rest APIs
~~~~~~~~~

This web server was developed to provide simple and powerfull Rest APIs.
By using this APIs you will be able to query, update, add and delete
your applications in this repository.

Born to be free
~~~~~~~~~~~~~~~

OpenFlow was born with a simple idea: make your network more vendor
agnostic and we like that!

We are advocates and supporters of free software and we believe that the
more eyes observe the code, the better it will be. This project can
receive support from many vendors, but will never follow a particular
vendor direction.

*napps-server* will always be free software.

Authors
-------

For a complete list of authors, please open ``AUTHORS.md`` file.

Contributing
------------

If you want to contribute to this project, please read
`CONTRIBUTE.md <CONTRIBUTE.md>`__ and `HACKING.md <HACKING.md>`__ files.

License
-------

This software is under *MIT-License*. For more information please read
``LICENSE`` file.

.. |Tag| image:: https://img.shields.io/github/tag/kytos/python-openflow.svg
   :target: https://github.com/kytos/python-openflow/tags
.. |Release| image:: https://img.shields.io/github/release/kytos/python-openvpn.svg
   :target: https://github.com/kytos/python-openflow/releases
.. |Tests| image:: http://kytos.io/imgs/tests-status.svg
   :target: https://github.com/kytos/python-openflow
.. |License| image:: https://img.shields.io/github/license/kytos/python-openflow.svg
   :target: https://github.com/kytos/python-openflow/blob/master/LICENSE
