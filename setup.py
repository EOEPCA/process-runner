import os
from setuptools import setup, find_packages

def package_files(where):
    paths = []
    for directory in where:
        for (path, directories, filenames) in os.walk(directory):
            for filename in filenames:
                paths.append(os.path.join(path, filename).replace('src/wps3_client/', ''))
    return paths


extra_files = package_files(['src/wps3_client/assets'])

console_scripts = """
[console_scripts]
wps3tool=wps3_client.wps3:entry
"""

setup(entry_points=console_scripts,
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      package_data={'': extra_files})

