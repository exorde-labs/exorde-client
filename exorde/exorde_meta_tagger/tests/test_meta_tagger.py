import pytest, json

from exorde_meta_tagger import meta_tagger_initialization, tag
from aiosow.autofill import autofill
from .sample import SAMPLE

CONFIG = meta_tagger_initialization()


def test_max_depth_is_set():
    assert CONFIG["max_depth"] == 2


@pytest.mark.asyncio
async def test_result_of_tag_should_be_json_serializable():
    """Result requires to be serialiable to pass trough the network."""
    test_content = SAMPLE[1:]
    result = await autofill(tag, args=[test_content], memory=CONFIG)
    json.dumps(result)
