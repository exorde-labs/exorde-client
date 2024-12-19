def print_dict_structure(d, indent=0, visited=None):
    """Recursively prints the structure of a dictionary.
    For lists, it prints the type of the first element and expands if it's a dict."""
    if visited is None:
        visited = set()
    indent_space = '    ' * indent
    obj_id = id(d)
    if obj_id in visited:
        print(f"{indent_space}<Recursion detected>")
        return
    visited.add(obj_id)

    if isinstance(d, dict):
        print(f"{indent_space}dict:")
        for key, value in d.items():
            print(f"{indent_space}    key: {key}")
            print_dict_structure(value, indent + 2, visited)
    elif isinstance(d, list):
        if d:
            first_elem = d[0]
            first_elem_type = type(first_elem).__name__
            print(f"{indent_space}list[{first_elem_type}]")
            if isinstance(first_elem, dict):
                # Expand the first dictionary in the list
                print_dict_structure(first_elem, indent + 1, visited)
            else:
                # For other types, we stop at the first element's type
                pass
        else:
            print(f"{indent_space}list[empty]")
    elif isinstance(d, tuple):
        if d:
            first_elem = d[0]
            first_elem_type = type(first_elem).__name__
            print(f"{indent_space}tuple[{first_elem_type}]")
            if isinstance(first_elem, dict):
                # Expand the first dictionary in the tuple
                print_dict_structure(first_elem, indent + 1, visited)
            else:
                pass
        else:
            print(f"{indent_space}tuple[empty]")
    else:
        print(f"{indent_space}{type(d).__name__}")


