"""Notify the user with spotting statistics"""
import argparse

from exorde.counter import AsyncItemCounter
from exorde.models import Ponderation
from exorde.notification import send_notification


async def statistics_notification(
    ponderation: Ponderation,
    counter: AsyncItemCounter,
    quota_layer: dict[str, float],
    only_layer: dict[str, float],
    command_line_arguments: argparse.Namespace,
):
    """
    - statistics_notification is called from the `brain.py` right
      after `print_counts`
    """
    rep = 0
    for item in ponderation.weights:
        rep += await counter.count_occurrences("rep_" + item)
    rep += await counter.count_occurrences("other")
    await send_notification(
        command_line_arguments,
        f"You collected {rep} unique posts over the last 24h",
    )


__all__ = ["statistics_notification"]
