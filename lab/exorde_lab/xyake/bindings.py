from aiosow.bindings import wire
from exorde_lab.xyake import (
    populate_keywords as populate_keywords_implementation,
)


keyword_extracted_triggered_on, on_keywords_extracted_do = wire(perpetual=True)

populate_keywords = keyword_extracted_triggered_on(
    populate_keywords_implementation
)
