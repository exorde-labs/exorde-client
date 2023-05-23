from exorde_data import query

from aiosow.bindings import alias, wire
from aiosow.routines import routine, infinite_generator
from exorde.scraping import generate_url

broadcast_formated_when, on_formated_data_do = wire()


alias("keyword")(lambda: "bitcoin")
alias("url")(generate_url)
scrap = infinite_generator(lambda: True)(query)
routine(0.2, perpetuate=False)(broadcast_formated_when(scrap))


__all__ = ["broadcast_formated_when", "on_formated_data_do"]
