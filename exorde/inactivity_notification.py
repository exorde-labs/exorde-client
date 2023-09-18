"""Notify user of inactive client"""

import argparse

from exorde.counter import AsyncItemCounter
from exorde.models import Ponderation
from exorde.notification import send_notification


async def inactivity_notification(
    ponderation: Ponderation,
    counter: AsyncItemCounter,
    command_line_arguments: argparse.Namespace,
) -> None:
    rep = 0
    for item in ponderation.weights:
        rep += await counter.count_occurrences("rep_" + item)
    rep += await counter.count_occurrences("other")
    if rep == 0:
        await send_notification(
            command_line_arguments,
            f"You didn't collect any post over the last 30 minutes",
        )


__all__ = ["inactivity_notification"]
