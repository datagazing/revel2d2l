=========
revel2d2l
=========


.. image:: https://img.shields.io/pypi/v/revel2d2l.svg
        :target: https://pypi.python.org/pypi/revel2d2l

.. image:: https://img.shields.io/travis/datagazing/revel2d2l.svg
        :target: https://travis-ci.com/datagazing/revel2d2l

.. image:: https://readthedocs.org/projects/revel2d2l/badge/?version=latest
        :target: https://revel2d2l.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status



Import Revel grade data into D2L LMS

Features
--------

* Converts Revel csv file to D2L csv file
* Matches user data based on a reference file from D2L and several heuristics
* Default options should probably just work, apart from which files to process
* See the command line utility usage message for description of heuristics
* The script is quiet apart from warnings by default (use -v for more info)

Examples
--------

.. code-block:: console

  revel2d2l -h  # Print usage message and exit
  revel2d2l -v -i revel.csv -u d2l_users.xlsx -o upload_this_to_d2l_grades.csv

License
-------

* Free software: MIT license

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
