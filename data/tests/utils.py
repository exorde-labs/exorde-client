import os, re


def get_package_name(setup_file_path):
    # Read the setup.py file as text
    with open(setup_file_path, "r") as file:
        content = file.read()

    # Use regular expressions to extract the package name
    package_name_match = re.search(r'name\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if package_name_match:
        package_name = package_name_match.group(1)
    else:
        raise ValueError("Package name not found in setup.py.")

    return package_name


def discover_packages(folder_path):
    result = []
    folders = os.listdir(folder_path)
    for folder in folders:
        setup_file = os.path.abspath(
            os.path.join("scraping/" + folder, "setup.py")
        )
        package_name = get_package_name(setup_file)
        result.append((folder, package_name))
    return result
