from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Caesar Trading Bot',
    version='0.1.0',
    description='A super simply and effective trading bot for our profit',
    long_description=readme,
    author='Roberto Nascimento Jr, Dimas Germano, Jorge Elô',
    author_email='robertonscjr@protonmail.com',
    url='https://github.com/robertonscjr',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
