"""Exorde drivers for meta_tagger"""
from aiosow.autofill import autofill, make_async
from exorde_meta_tagger import (
    zero_shot as zero_shot_implementation,
    tag as tag_implementation,
)


async def zero_shot(item, memory):
    """
    Translate items for zero_shot's expectations (dict -> str)
    Sets zero_shot result at item['Analytics']
    """
    zero_shot_result = await autofill(
        make_async(zero_shot_implementation),
        args=[[item["item"]["Content"]]],
        memory=memory,
    )
    item["item"]["Analytics"] = zero_shot_result
    return item


async def tag(items, memory):
    tag_results = await autofill(
        make_async(tag_implementation),
        args=[[item["item"]["Content"] for item in items]],
        memory=memory,
    )
    for item, result in zip(items, tag_results):
        item["tags"] = result
    return items


__all__ = ["zero_shot", "tag"]
