import logging
from argostranslate import package
from typing import cast


if __name__ == "__main__":
    """Download and install Argos Translate translation packages"""
    package.update_package_index()
    available_packages = package.get_available_packages()
    length = len(available_packages)
    logging.info(f"{length} translation modules to install")
    i = 0
    for pkg in available_packages:
        i += 1
        print(
            f" - installing translation module ({i}/{length}) : ({str(pkg)})"
        )

        # cast used until this is merged https://github.com/argosopentech/argos-translate/pull/329
        package.install_from_path(
            cast(package.AvailablePackage, pkg).download()
        )
