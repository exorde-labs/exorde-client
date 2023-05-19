from setuptools import find_packages, setup

setup(
    name="exorde_data",
    version="0.0.1",
    packages=find_packages(include="exorde_data"),
    install_requires=["jschemator", "aiosow"],
    entry_points={
        "console_scripts": ["exorde_data = exorde_data.__init__:print_schema"]
    },
    extras_require={"reddit": ["1p98j3envoubi3fco1kc"], "dev": ["pytest"]},
)
