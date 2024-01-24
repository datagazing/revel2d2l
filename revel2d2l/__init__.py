"""
Import Revel grade data into D2L LMS

Features
--------

* Converts Revel csv file to D2L csv file
* Matches user data based on a reference file from D2L and several heuristics
* Default options should probably just work, apart from which files to process
* See the command line utility usage message for description of heuristics
* The script is quiet apart from warnings by default (use -v for more info)
* Options can be specified in a yaml config file: ~/.revel2d2l.yaml
    * The most useful of which might be the users file

Examples
--------

.. code-block:: console

  revel2d2l -h  # Print usage message and exit

  revel2d2l -v -i revel.csv -u d2l_users.xlsx -o upload_this_to_d2l_grades.csv

.. code-block:: yaml

  users: '~/Some Place/users.xlsx'

License
-------

* Free software: MIT license

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

"""

__author__ = """Brendan Strejcek"""
__email__ = 'brendan@datagazing.com'
__version__ = '0.1.0'

from .revel2d2l import main  # noqa F401
