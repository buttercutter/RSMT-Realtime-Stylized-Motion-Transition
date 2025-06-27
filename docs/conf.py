# RSMT Documentation Configuration
# Configuration file for Sphinx documentation

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "rsmt"))

# Project information
project = "RSMT"
copyright = "2024, RSMT Development Team"
author = "RSMT Development Team"
release = "1.0.0"
version = "1.0"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.githubpages",
    "sphinx.ext.mathjax",
    "myst_parser",
    "sphinx_autodoc_typehints",
]

# Source files
source_suffix = {
    ".rst": None,
    ".md": "myst_parser",
}

master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Language and encoding
language = "en"
html_theme_options = {"navigation_depth": 4}

# HTML output
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "canonical_url": "",
    "analytics_id": "",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#2980B9",
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_context = {
    "display_github": True,
    "github_user": "rsmt-project",
    "github_repo": "rsmt",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_js_files = ["custom.js"]

# HTML customization
html_title = f"{project} v{release}"
html_short_title = project
html_logo = "_static/logo.png"
html_favicon = "_static/favicon.ico"

html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        "donate.html",
    ]
}

# Autodoc configuration
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "special-members": "__init__",
    "private-members": False,
    "inherited-members": True,
}

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# Napoleon configuration (for Google/NumPy style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autosummary configuration
autosummary_generate = True
autosummary_generate_overwrite = True

# Intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "torch": ("https://pytorch.org/docs/stable/", None),
    "lightning": ("https://lightning.ai/docs/pytorch/stable/", None),
}

# TODO configuration
todo_include_todos = True

# Coverage configuration
coverage_show_missing_items = True

# LaTeX output
latex_engine = "pdflatex"
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": "",
    "fncychap": "\\usepackage[Bjornstrup]{fncychap}",
    "printindex": "\\footnotesize\\raggedright\\printindex",
}

latex_documents = [
    (master_doc, "rsmt.tex", "RSMT Documentation", "RSMT Development Team", "manual"),
]

# Manual page output
man_pages = [
    (master_doc, "rsmt", "RSMT Documentation", [author], 1)
]

# Texinfo output
texinfo_documents = [
    (
        master_doc,
        "rsmt",
        "RSMT Documentation",
        author,
        "rsmt",
        "Real-time Stylized Motion Transition framework",
        "Miscellaneous",
    ),
]

# EPUB output
epub_title = project
epub_exclude_files = ["search.html"]

# MyST configuration
myst_enable_extensions = [
    "deflist",
    "tasklist",
    "colon_fence",
    "fieldlist",
    "attrs_inline",
    "attrs_block",
]

myst_heading_anchors = 3
myst_url_schemes = ["http", "https", "mailto"]

# Custom configuration
def setup(app):
    """Sphinx setup function."""
    app.add_css_file("custom.css")
    app.add_js_file("custom.js")
    
    # Add custom directives or roles here
    pass
