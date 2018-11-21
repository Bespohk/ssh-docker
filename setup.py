# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
import sshdocker

path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(path, 'requirements.txt')) as f:
    requirements = f.read().splitlines()

with open(os.path.join(path, 'LICENSE')) as f:
    license = f.read()

with open(os.path.join(path, 'README.rst')) as f:
    readme = f.read()

setup(
    name='ssh-docker',
    version=sshdocker.__version__,
    description='Utility methods for dealing with HTML.',
    long_description=readme,
    license=license,
    author='Simon Coulton',
    author_email='simon@bespohk.com',
    py_modules=['sshdocker'],
    platforms=['Python 3.7'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['docker',
              'python3',
              'ssh',
              'cli'],
    install_requires=requirements,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    entry_points="""
        [console_scripts]
        ssh-docker=sshdocker.api:main
    """,
)
