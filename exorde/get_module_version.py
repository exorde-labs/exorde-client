import pkg_resources


def get_module_version(module_name) -> str:
    try:
        # Use pkg_resources to retrieve the distribution object for the module
        distribution = pkg_resources.get_distribution(module_name)

        # Get the version from the distribution object
        module_version = distribution.version

        return module_version
    except Exception as e:
        return f"Unable to retrieve version for {module_name}: {str(e)}"
