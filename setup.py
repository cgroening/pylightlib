from setuptools import setup, find_packages


setup(
    name='pylightlib',
    version='0.1.0',
    packages=find_packages(include=[
        'io', 'math', 'mech', 'msc', 'qt', 'tk', 'txtl'
    ]),
    install_requires=[],
)