from setuptools import setup, find_packages

setup(
    name='exorde',
    version='0.1.0',
    packages=find_packages(include=['exorde']),
    license='MIT',
    install_requires=[
        'pyyaml',
        'aiosow_twitter',
        'web3'
    ],
)
