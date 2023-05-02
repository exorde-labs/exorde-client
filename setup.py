import os, ast
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()


def extract_install_requires(path):
    install_requires = set()

    for root, dirs, files in os.walk(path):
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")

        for filename in files:
            if filename == "setup.py":
                setup_file = os.path.join(root, filename)
                with open(setup_file, "r") as f:
                    try:
                        tree = ast.parse(f.read(), setup_file)
                    except SyntaxError:
                        continue

                call_exprs = [
                    node
                    for node in tree.body
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                ]
                call_exprs = [
                    call
                    for call in call_exprs
                    if hasattr(call.value.func, "id") and call.value.func.id == "setup"
                ]

                for call_expr in call_exprs:
                    keywords = call_expr.value.keywords
                    for keyword in keywords:
                        if keyword.arg == "install_requires":
                            reqs = keyword.value.elts
                            for req in reqs:
                                req_str = req.s
                                if req_str:
                                    install_requires.add(req_str)
    install_requires = [req for req in install_requires if "exorde" not in req]
    return list(install_requires)


setup(
    name="exorde",
    version="0.1.1",
    description="Exorde CLI",
    packages=find_packages(
        include=[
            "exorde",
            "exorde.spotting",
            "exorde.validation",
            "exorde.xyake",
            "exorde.reddit",
            "exorde.twitter",
            "exorde.ipfs",
        ]
    ),
    include_package_data=True,
    license="MIT",
    entry_points={
        "console_scripts": [
            "exorde = exorde.__init__:launch",
        ],
    },
    install_requires=extract_install_requires("./exorde"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires="==3.10.*",
)
