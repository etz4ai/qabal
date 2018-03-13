from setuptools import setup

# Boilerplate for integrating with PyTest
from setuptools.command.test import test
import sys


class PyTest(test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]
    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

# The actual setup metadata
setup(
    name='qabal',
    version='0.0.2',
    description='A fast and simple message broker with content-based routing.',
    long_description=open("README.md").read(),
    keywords='broker routing content_based',
    author='JJ Ben-Joseph',
    author_email='opensource@phrostbyte.com',
    python_requires='>=3.6',
    url='https://www.phrostbyte.com/',
    license='Apache',
    classifiers=[
        'Topic :: Communications',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent'
    ],
    py_modules=['qabal'],
    tests_require=['pytest'],
    cmdclass = {'test': PyTest}
)