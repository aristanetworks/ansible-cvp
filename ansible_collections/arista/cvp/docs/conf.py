# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import corlab_theme
import sphinxbootstrap4theme
from PSphinxTheme import utils
import os
import sys
import recommonmark
from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))
sys.path.insert(2, os.path.abspath(
    '../ansible_collections/arista/cvp/roles/dhcp_configuration/'))

# Import ansible2rst so that RST files can be generated.
import ansible2rst
# Call ansible2rst.main() to generate RST files.
ansible2rst.main()


def setup(app):
    app.add_config_value('recommonmark_config', {
        'enable_math': True,
        'enable_eval_rst': True,
        'enable_auto_doc_ref': True,
        'auto_code_block': True,
        # 'url_resolver': lambda url: github_doc_root + url,
        'auto_toc_tree_section': 'Contents',
    }, True)
    app.add_transform(AutoStructify)


# -- Project information -----------------------------------------------------

project = 'Arista CloudVision ansible collection'
copyright = '2020, Arista Ansible Team'
author = 'Arista Ansible Team'

# The full version, including alpha/beta/rc tags
release = '1.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'recommonmark'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'AnsiblewithAristadevicesdoc'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

#---sphinx-themes-----
# html_theme = 'p-main_theme'
# p, html_theme, needs_sphinx = utils.set_psphinxtheme(html_theme)
# html_theme_path = p


#---sphinx-themes-----
# html_theme = 'sphinxbootstrap4theme'
# html_theme_path = [sphinxbootstrap4theme.get_path()]

# html_theme = 'pyramid'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}
# html_theme = 'sphinx_rtd_theme'

# ...
html_theme = 'corlab_theme'
html_theme_path = [corlab_theme.get_theme_dir() ]
