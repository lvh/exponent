import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

packageName = "exponent"

import re
versionLine = open(packageName + "/_version.py", "rt").read()
match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", versionLine, re.M)
versionString = match.group(1)

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

setup(name=packageName,
      version=versionString,
      description='An experimental toolkit for applications with a fractal architecture',
      long_description=open("README.rst").read(),
      url='https://github.com/lvh/' + packageName,

      author='Laurens Van Houtven',
      author_email='_@lvh.cc',

      packages=["exponent", "exponent.test"],
      test_suite="exponent.test",
      cmdclass={'test': Tox},
      zip_safe=True,

      license='ISC',
      keywords="fractal-architectures twisted axiom",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Twisted",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python :: 2 :: Only",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7"
        ]
)
