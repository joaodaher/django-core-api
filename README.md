![Github CI](https://github.com/joaodaher/django-core-api/workflows/Github%20CI/badge.svg)
[![python](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/)
[![django](https://img.shields.io/badge/django-3-green.svg)](https://www.djangoproject.com/)
# Django Core API

This Django Core API allows APIs to follow predefined styleguide and remove a bunch of boilerplate code from them.

The implemented features are all in the [Wiki](https://github.com/joaodaher/django-core-api/wiki).


## Setup
  - clone this project
  - install [Pyenv](https://github.com/pyenv/pyenv#installation)
  - install the project's Python version: `pyenv install`
  - install dependencies: `make dependencies`


### Deploy an Alpha version of this project
  - clone this project
  - update version with a `aN` as suffix (eg. `1.2.3a1`)
  - remove build files: `make clean`
  - deploy to PyPi: `make publish`
