from setuptools import setup, find_packages


setup(
    name='exc_exorde',
    version='0.1.0',
    packages=find_packages(include=['exc_exorde']),
    license='MIT',
    install_requires=[
        'exc_twitter',
        'web3'
    ],
)
