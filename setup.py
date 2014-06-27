
from setuptools import setup, find_packages

setup(
    name = 'wsgitester',
    version = '2.0',
    description = 'Test WSGI Gateways',
    author = 'Robin Schoonover',
    author_email = 'robin@cornhooves.org',
    license = 'MIT',
    packages = find_packages('.'),
    entry_points = {
        'console_scripts': [
            'wsgitester = wsgitester.client:main'
        ],
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ]
)