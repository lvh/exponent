from distutils.core import setup

import re
versionLine = open("exponent/_version.py", "rt").read()
match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", versionLine, re.M)
versionString = match.group(1)

setup(name='exponent',
      version=versionString,
      description='An experimental toolkit for building applications with a fractal architecture',
      url='https://github.com/lvh/exponent',

      author='Laurens Van Houtven',
      author_email='_@lvh.cc',

      packages=["exponent", "exponent.test"],

      license='ISC',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Twisted",
        "License :: OSI Approved :: ISC License (ISCL)",
        ]
)
