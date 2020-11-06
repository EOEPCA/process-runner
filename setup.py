from setuptools import setup, find_packages
from io import open
import os

console_scripts = """
[console_scripts]
wps3=module.wps3:main
"""

setup(entry_points=console_scripts,
      packages=find_packages(where='src'),
      package_dir={'': 'src'})

