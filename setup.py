import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='ifmo-xblock-scilab',
    version='0.1',
    install_requires=[
        'django',
        'path.py',
        'requests',
        'python-dateutil',
        'xblock'
    ],
    packages=['xblock_scilab', 'xblock_ifmo'],
    include_package_data=True,
    license='BSD License',
    description='Package provides ifmo courses specific modules.',
    long_description=README,
    url='http://www.de.ifmo.ru/',
    author='Dmitry Ivanyushin',
    author_email='d.ivanyushin@cde.ifmo.ru',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', 
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    entry_points={
        'xblock.v1': [
            'ifmo_xblock_scilab = xblock_scilab:ScilabXBlock',
        ]
    },
)
