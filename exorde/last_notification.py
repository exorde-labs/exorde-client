"""last_notification is a string contained in LiveConfiguration"""

import logging
import argparse
from typing import Callable

from exorde.persist import PersistedDict
from exorde.notification import send_notification
from exorde.models import LiveConfiguration


def build_last_notification() -> Callable:
    persisted_last_notification = PersistedDict(
        "/tmp/exorde/last_notification.json"
    )

    async def last_notification(
        live_configuration: LiveConfiguration,
        command_line_arguments: argparse.Namespace,
    ) -> None:
        last_notification = live_configuration.get("last_notification", None)
        if not last_notification:
            logging.warning("no last_notification found in LiveConfiguration")
            return
        nonlocal persisted_last_notification
        if (
            persisted_last_notification["last_notification"] == None
            or persisted_last_notification["last_notification"]
            != last_notification
        ):
            await send_notification(command_line_arguments, last_notification)
            persisted_last_notification[
                "last_notification"
            ] = last_notification

    return last_notification


last_notification = build_last_notification()

__all__ = ["last_notification"]
