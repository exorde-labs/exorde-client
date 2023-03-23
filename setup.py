from setuptools import setup, find_packages

setup(
    name='exorde',
    version='0.1.0',
    packages=find_packages(include=['exorde']),
    license='MIT',
    entry_points={
        'console_scripts': [
            'exorde = exorde.__init__:launch',
        ],
    },
    install_requires=[
        'python-dateutil',
        'pyyaml',
        'aiosow',
        'aiosow_twitter',
        'web3'
    ],
)
