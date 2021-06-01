from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='signinghub-api',
    version='0.1.0',
    description='Package with default calls for the SigningHub API',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Erwin Mintiens',
    author_email='erwin.mintiens@gmail.com',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=['requests']
)
