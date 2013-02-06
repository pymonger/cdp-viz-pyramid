import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.txt")).read()
CHANGES = open(os.path.join(here, "CHANGES.txt")).read()

entry_points = """\
    [paste.app_factory]
    main = cdp_viz:main

    [paste.app_install]
    main = paste.script.appinstall:Installer
"""

setup(name="cdp_viz",
      version="0.0",
      description="cdp_viz",
      long_description=README + "\n\n" +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author="",
      author_email="",
      url="",
      keywords="web pyramid pylons",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite="cdp_viz",
      entry_points=entry_points,
      paster_plugins=["pyramid"],
      )

