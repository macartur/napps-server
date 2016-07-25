# Napps-Server

[![Tag][tag-icon]][tag-url]
[![Release][release-icon]][release-url]
[![Tests][tests-icon]][tests-url]
[![License][license-icon]][license-url]

*napps-server* is an application repository to store and manage SDN 
applications which runs on top of kytos controller. A command line is 
provided with kytos to querie and install applications easily. 

This web server is part of *Kytos* project and was developed to share, 
find and reuse SDN applications. A REST API is provided to perform 
queries and install applications.

For more information about, please visit our [Kytos web site]
[kytos-url].

## Installing

### Dependences

In order to install Napps-Server and create a SDN repository for your 
application you must install [REDIS database][redis-install-url] 

### Naps-Server Installation

You can install this package from source or via pip. If you have cloned 
this repository and want to install it via `setuptools`, please run:

```bash
sudo python3 setup.py install
```

Or, to install via pip, please execute:

```bash
sudo pip3 install napps-server
```

### REDIs Installation

For installing REDIs you can follow [Redis Quick Start]
[redis-install-url] guide for details. Also we provide an small REDIs 
schema to be used for testing the installation. To install the REDIs 
schema, run the command:

```bash
cd to_REDIs_Installation_dir
cd src/
cat napps_server_git_repo_dir/schema_redis.nosql | ./redis-cli
```

## Main Highlights

### Speed focused

We keep the word *performance* in mind since the beginning of the 
development. Also, as computer scientists, we will always try to get the 
best performance by using the most suitable algorithms.

### Rest APIs

This web server was developed to provide simple and powerfull Rest APIs. 
By using this APIs you will be able to query, update, add and delete 
your applications in this repository. 

### Born to be free

OpenFlow was born with a simple idea: make your network more vendor 
agnostic and we like that!

We are advocates and supporters of free software and we believe that the 
more eyes observe the code, the better it will be. This project can 
receive support from many vendors, but will never follow a particular 
vendor direction.

*napps-server* will always be free software.

## Authors

This is a collaborative project between SPRACE (From São Paulo State 
University, Unesp) and Caltech (California Institute of Technology). 
For a complete list of authors, please open `AUTHORS.md` file.

## Contributing

If you want to contribute to this project, please read
[CONTRIBUTE.md](CONTRIBUTE.md) and [HACKING.md](HACKING.md) files.

## License

This software is under _MIT-License_. For more information please read 
`LICENSE` file.

[api-reference-url]: http://docs.kytos.io/python-openflow/api-reference/
[kytos-url]: http://kytos.io/
[redis-install-url]: http://redis.io/topics/quickstart
[of-url]: https://www.opennetworking.org/images/stories/downloads/sdn-resources/onf-specifications/openflow/openflow-spec-v1.0.0.pdf
[tag-icon]: https://img.shields.io/github/tag/kytos/python-openflow.svg
[tag-url]: https://github.com/kytos/python-openflow/tags
[release-icon]: https://img.shields.io/github/release/kytos/python-openvpn.svg
[release-url]: https://github.com/kytos/python-openflow/releases
[tests-icon]: http://kytos.io/imgs/tests-status.svg
[tests-url]: https://github.com/kytos/python-openflow
[license-icon]: https://img.shields.io/github/license/kytos/python-openflow.svg
[license-url]: https://github.com/kytos/python-openflow/blob/master/LICENSE
