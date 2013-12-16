# -*- coding: utf-8 -*-

import sys
import os

VERSION = '0.1.0dev'

extensions = []

templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'

project = u'Brewmeister'
copyright = u'2013, Matthias Vogelgesang'
version = VERSION
release = VERSION

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
