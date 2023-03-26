"""
Composition for EXD Mining.

TODOS:
    - check for main eth address
    - cache
    - smoother request frequency
"""


from aiosow.bindings import setup
from aiosow.routines import spawn_consumer

setup(spawn_consumer)
