"""Setup file for backward compatibility.

Modern projects should use pyproject.toml (PEP 621).
This file is only needed for older tools that don't support pyproject.toml.
"""

from setuptools import setup

# All configuration is in pyproject.toml
setup()
