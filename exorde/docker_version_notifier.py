"""notify user of new docker image version"""

import os
import logging
import argparse

from typing import Callable

from exorde.persist import PersistedDict
from exorde.notification import send_notification
from exorde.models import LiveConfiguration


def build_docker_version_notifier() -> Callable:
    last_notified_version = PersistedDict(
        "/tmp/exorde/docker_version_notification.json"
    )

    async def docker_version_notifier(
        live_configuration: LiveConfiguration,
        command_line_arguments: argparse.Namespace,
    ) -> None:
        current_img_version = os.environ.get("EXORDE_DOCKER_IMG_VERSION", None)
        """set during build time"""

        if not current_img_version:
            """does nothing if no image version is specified in env"""
            return

        """else check the version and notify the user"""

        nonlocal last_notified_version
        """last version the user has been notified for"""

        live_version = live_configuration.get("docker_version", None)
        """and docker version is specified by the network"""
        if not live_version:
            logging.warning("no docker version specified in LiveConfiguration")
            return

        if live_version != current_img_version:
            """notify"""
            if (
                last_notified_version["last_notification"] == None
                or last_notified_version != live_version
            ):
                await send_notification(
                    command_line_arguments, "A new exorde image is available"
                )
                last_notified_version["last_notification"] = live_version

    return docker_version_notifier


docker_version_notifier = build_docker_version_notifier()

__all__ = ["docker_version_notifier"]
