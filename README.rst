
wsgitester
==========

wsgitester is a test suite for WSGI gateways.  It's implemented as two
parts include a WSGI application and a web client.

Installing
==========

wsgitester uses a setup.py script in the usual fashion, like so::

    $ python ./setup.py install

Using wsgitester inside virtualenv or venv is recommended.

Running the WSGI Application
============================

Deployment of the WSGI application is dependant on the WSGI gateway being
tested.  In any case, the location of the application entry point is
located in MODULE:OBJECT notation at ``wsgitester.wsgi:application``.

For example, to test wsgiref's reference server::

    from wsgiref.simple_server import make_server
    from wsgitester.wsgi import application

    server = make_server('', 8000, application)
    server.serve_forever()

Running the Tests
=================

Once the WSGI application is deployed, the tests proper may be run.

The test script is installed as ``wsgitester``, but may also be run
as a python module as ``python -m wsgitester.client``.

Minimal usage requires the URL that maps to deployed WSGI application.
In the example above, that url would be http://localhost:8000/, so 
the tests would be run like this::

    $ wsgitester http://localhost:8000/
