from distutils.core import setup

setup(name='exponent',
      version='20121001',
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

