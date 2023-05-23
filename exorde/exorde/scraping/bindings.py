from exorde_data import query

from aiosow.bindings import alias
from aiosow.routines import routine, infinite_generator
from exorde.formated import broadcast_formated_when
from . import generate_url

alias("url")(generate_url)
scrap = infinite_generator(lambda: True)(query)
routine(0.2, perpetuate=False)(broadcast_formated_when(scrap))
