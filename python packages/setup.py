from setuptools import *
import flamechess

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name="flamechess",
      version=flamechess.__version__,
      author="ZHC 张瀚宸",
      author_email="bjhansen2012@outlook.com",
      description="Flamechess Tools",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/zhc7/chess",
      packages=find_namespace_packages(),
      install_requires=["requests"],
      classifiers=[
          "Environment :: Console",
          "Programming Language :: Python :: 3.8",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Programming Language :: Python :: 3"
      ],
      python_requires=">=3.4.0",
      )
