import ast
import os
import sys


def extract_imports_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read(), filename=file_path)
            import_nodes = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                or isinstance(node, ast.ImportFrom)
            ]
            imports = []
            for node in import_nodes:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
            return imports
        except SyntaxError:
            return []


def find_python_files(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def main(directory):
    python_files = find_python_files(directory)
    all_imports = {}
    for file_path in python_files:
        file_as_module = file_path
        file_as_module = file_as_module.replace("/", ".")
        file_as_module = file_as_module.replace(".py", "")
        imports = extract_imports_from_file(file_path)
        if imports:
            all_imports[file_as_module] = imports

    for file_path, imports in all_imports.items():
        print(f"File: {file_path}")
        print("Imports:")
        for imp in imports:
            print(f"\t{imp}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <directory_path>")
    else:
        directory_path = sys.argv[1]
        main(directory_path)
