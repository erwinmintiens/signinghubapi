from setuptools import setup, find_packages

setup(
    name='signinghub-api',
    version='0.1.0',
    description='Package with default calls for the SigningHub API',
    author='Erwin Mintiens',
    author_email='erwin.mintiens@gmail.com',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=['requests']
)
