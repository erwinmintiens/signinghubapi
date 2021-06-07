from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='signinghubapi',
    version='0.1.0',
    description='Package with default calls for the SigningHub API',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/erwinmintiens/signinghub-api',
    author='Erwin Mintiens',
    author_email='erwin.mintiens@gmail.com',
    keywords=['SigningHub', 'API'],
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=['requests'],
    license_files=('LICENSE',),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License"
    ]
)
