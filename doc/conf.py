#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Survey of Commonly Available C Header Files
# documentation build configuration file.
#
# Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# There is NO WARRANTY.

import sys
import os

sys.path.insert(0, os.path.abspath('../sphinx/ext'))

project   = 'Survey of Commonly Available C Header Files'
copyright = '2013–2014, Zack Weinberg and other contributors'
version   = '1.1'
release   = '1.1'
today     = 'January 5, 2014'

html_title = project
html_short_title = 'C Headers Survey'

needs_sphinx = '1.2'
extensions = [
    'sphinx.ext.todo',
    'doc_comments',
    'html5_output',
    'objects',
]

source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['*~']
html_show_sourcelink = False
html_translator_class = 'html5_output.SmartyPantsHTML5Translator'

# - Things that might get changed later.

# currently we have nothing to put in the commented-out directories
#templates_path   = ['../sphinx/templates']
html_static_path = ['../sphinx/static']
html_theme_path = ['../sphinx/theme']
#html_extra_path = ['../sphinx/extra']

# While this is a draft...
keep_warnings = True
todo_include_todos = True

html_theme = 'hsv'
#html_theme_options = {}
#html_logo = None
#html_favicon = None
pygments_style = 'sphinx.pygments_styles.PyramidStyle'

# Indexing is disabled until we figure out just what should be indexed.
html_use_index = False
html_domain_indices = False
#html_split_index = False
