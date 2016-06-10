# Napps-Server

[![Openflow][of-icon]][of-url]
[![Tag][tag-icon]][tag-url]
[![Release][release-icon]][release-url]
[![Tests][tests-icon]][tests-url]
[![License][license-icon]][license-url]

*napps-server* is an application repository to store and manage SDN applications 
which runs on top of kytos controller. A command line is provided with kytos
to querie and install applications easily. 

This web server is part of *Kytos* project and was developed to share, find and
reuse SDN applications. A REST API is provided to perform queries and install
applications.

For more information about, please visit our [Kytos web site][kytos-url].

## Installing

### Dependences

In order to install Napps-Server and create a SDN repository for your application
you must install [REDIS database][redis-install-url] 

### Naps-Server Installation

You can install this package from source or via pip. If you have cloned this
repository and want to install it via `setuptools`, please run:

```shell
sudo python3 setup.py install
```

Or, to install via pip, please execute:

```shell
sudo pip3 install napps-server
```

## Usage

In order to deploy a small *naps-server*, you must start Redis database on
your localhost and listen in the default port 6379. Please refer to the
[Redis Quick Start][redis-install-url] guide for details.

After Redis startup, populate the database with a small dataset located
in our repository (napps-server/tests/dataset.redis) as follow:
```bash
cat napps-server/tests/dataset.redis | redis-cli
````
Now, start the web server:
```bash
python3 run.py
````
You can now point your web browser to the url http://127.0.0.0:5000/apps/. It 
is expected to see a JSON structured document, describing all applications.

## Main Highlights

### Speed focused

We keep the word *performance* in mind since the beginning of the development.
Also, as computer scientists, we will always try to get the best performance by
using the most suitable algorithms.

### Rest APIs

This web server was developed to provide simple and powerfull Rest APIs. By using
this APIs you will be able to query, update, add and delete your applications
in this repository. 

### Born to be free

OpenFlow was born with a simple idea: make your network more vendor agnostic
and we like that!

We are advocates and supporters of free software and we believe that the more
eyes observe the code, the better it will be. This project can receive support
from many vendors, but will never follow a particular vendor direction.

*napps-server* will always be free software.

## Authors

This is a collaborative project between SPRACE (From São Paulo State University,
Unesp) and Caltech (California Institute of Technology). For a complete list of
authors, please open `AUTHORS.md` file.

## Contributing

If you want to contribute to this project, please read
[CONTRIBUTE.md](CONTRIBUTE.md) and [HACKING.md](HACKING.md) files.

## License

This software is under _MIT-License_. For more information please read `LICENSE`
file.

[api-reference-url]: http://docs.kytos.io/python-openflow/api-reference/
[kytos-url]: http://kytos.io/
[redis-install-url]: http://redis.io/topics/quickstart
[of-icon]: https://img.shields.io/badge/Openflow-1.0.0-brightgreen.svg
[of-url]: https://www.opennetworking.org/images/stories/downloads/sdn-resources/onf-specifications/openflow/openflow-spec-v1.0.0.pdf
[tag-icon]: https://img.shields.io/github/tag/kytos/python-openflow.svg
[tag-url]: https://github.com/kytos/python-openflow/tags
[release-icon]: https://img.shields.io/github/release/kytos/python-openvpn.svg
[release-url]: https://github.com/kytos/python-openflow/releases
[tests-icon]: http://kytos.io/imgs/tests-status.svg
[tests-url]: https://github.com/kytos/python-openflow
[license-icon]: https://img.shields.io/github/license/kytos/python-openflow.svg
[license-url]: https://github.com/kytos/python-openflow/blob/master/LICENSE
