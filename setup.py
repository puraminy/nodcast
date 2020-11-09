import setuptools
import os, sys

with open("README.md", "r") as fh:
    long_description = fh.read()

reqs = [i.strip() for i in open("requirements.txt").readlines()]
reqs = ["requests", "appdirs"]
if os.name == "nt" or sys.platform.lower().startswith("win"):
     reqs += ['windows-curses']
setuptools.setup(
    name="nodcast", # Replace with your own username
    version="0.1.0",
    author="A Pouramini",
    author_email="pouramini@gmail.com",
    description="NodCast, a text-based article reader and manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/puraminy/nodcast",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'nodcast = nodcast.nodcast:main',
        ],
    },
    install_requires=reqs,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
