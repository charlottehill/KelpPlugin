import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = [
    'hairball>=0.2'
    ]

setup(name='kelp',
      version='0.0',
      description='kelp',
      long_description=README,
      classifiers=["Programming Language :: Python"],
      author='Charlotte Hill',
      author_email='charlotte@hillnetwork.com',
      url='https://github.com/charlottehill/KelpPlugin',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      kelp = kelp.offline:main
      """,
      )
