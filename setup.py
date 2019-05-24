from distutils.core import setup

VERSION = '0.1'

setup(
    name='PNL',
    version=VERSION,
    packages=['PNL'],
    download_url='https://github.com/Novidys/pnl',
    license='',
    author='CyrilleFranchet',
    author_email='cyrille.franchet@novidys.com',
    description='Script to parse new leak files',
    scripts=['bin/pnl'],
    package_data={
        'pnl': ['VERSION'],
    },
    python_requires='>=3.6.*, <4',
    install_requires=[
        'chardet',
        'redis'
    ])
