# -*- coding: utf-8 -*-

import sys
import os
from pkg_resources import get_distribution

dist = get_distribution('brewmeister')

extensions = ['sphinxcontrib.httpdomain']

templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'

project = u'Brewmeister'
copyright = u'2013, Matthias Vogelgesang'
version = dist.version
release = dist.version

exclude_patterns = ['_build']
pygments_style = 'sphinx'

html_theme = 'default'
html_static_path = ['_static']
html_use_smartypants = True
htmlhelp_basename = 'Brewmeisterdoc'

latex_elements = {
    'papersize': 'a4paper',
}

latex_documents = [
  ('index', 'Brewmeister.tex', u'Brewmeister Documentation',
   u'Matthias Vogelgesang', 'manual'),
]

man_pages = [
    ('index', 'brewmeister', u'Brewmeister Documentation',
     [u'Matthias Vogelgesang'], 1)
]

texinfo_documents = [
  ('index', 'Brewmeister', u'Brewmeister Documentation',
   u'Matthias Vogelgesang', 'Brewmeister', 'One line description of project.',
   'Miscellaneous'),
]
