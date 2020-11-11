import os
from setuptools import setup, find_packages

def package_files(where):
    paths = []
    for directory in where:
        for (path, directories, filenames) in os.walk(directory):
            for filename in filenames:
                paths.append(os.path.join(path, filename).replace('src/module/', ''))
    return paths


extra_files = package_files(['src/module/assets'])

console_scripts = """
[console_scripts]
wps3tool=module.wps3:main
"""

setup(entry_points=console_scripts,
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      package_data={'': extra_files})

