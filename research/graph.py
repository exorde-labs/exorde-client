import ast
import os
import sys
import json
from dataclasses import dataclass
import networkx as nx
import matplotlib.pyplot as plt


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


def extract_imports(directory) -> dict[str, list[str]]:
    python_files = find_python_files(directory)
    all_imports = {}
    for file_path in python_files:
        file_as_module = file_path
        file_as_module = file_as_module.replace("/", ".")
        file_as_module = file_as_module.replace(".py", "")
        imports = extract_imports_from_file(file_path)
        if imports:
            all_imports[file_as_module] = imports

    return all_imports


def f(key, import_map):
    return [1 if _key in import_map[key] else 0 for _key in import_map.keys()]


def dfs(matrix, visited, node, current_group):
    visited[node] = True
    current_group.append(node)

    for i in range(len(matrix)):
        if matrix[node][i] == 1 and not visited[i]:
            dfs(matrix, visited, i, current_group)


def find_connected_components(matrix):
    num_entities = len(matrix)
    visited = [False] * num_entities
    groups = []

    for i in range(num_entities):
        if not visited[i]:
            current_group = []
            dfs(matrix, visited, i, current_group)
            groups.append(current_group)

    return groups


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <directory_path>")
    else:
        directory_path = sys.argv[1]
        import_map = extract_imports(directory_path)

        print(json.dumps(import_map, indent=4))

        d = {}
        m = []
        i = 0
        for key in import_map:
            connections = f(key, import_map)
            m.append(connections)
            d[i] = {
                "position": i,
                "connections": connections,
                "name": key,
                "group": [],
            }
            # print(f"{key[:15]}\t\t: ({i}) {m[i]}")
            i = i + 1

        connected_components = find_connected_components(m)

        i = 0
        for group in connected_components:
            for id in group:
                d[id]["group"].append(i)
            i = i + 1

        for id in d:
            # print(d[id]["group"])
            pass

        i = 0
        for group in connected_components:
            for a in group:
                print(f'{d[a]["name"]} : {i}')
            i = i + 1
        print(connected_components)

        G = nx.Graph()

        # Add nodes and edges based on connected components
        for group in connected_components:
            for a in group:
                G.add_node(d[a]["name"])
                for b in group:
                    if a != b and m[a][b] == 1:
                        G.add_edge(d[a]["name"], d[b]["name"])

        # Draw the graph
        pos = nx.spring_layout(
            G
        )  # You can change the layout algorithm if needed
        plt.figure(figsize=(10, 8))
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_size=2000,
            node_color="skyblue",
            font_size=12,
            font_weight="bold",
        )
        plt.title("Connected Components of Python Files")
        plt.show()
