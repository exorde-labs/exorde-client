import argparse
import re
import logging
import os


def write_env(email, password, username, http_proxy=""):
    # Check the conditions for each field
    if email is None or len(email) <= 3:
        logging.info("write_env: Invalid email. Operation aborted.")
        return
    if password is None or len(password) <= 3:
        logging.info("write_env: Invalid password. Operation aborted.")
        return
    if username is None or len(username) <= 3:
        logging.info("write_env: Invalid username. Operation aborted.")
        return

    # Define the content
    content = f"SCWEET_EMAIL={email}\nSCWEET_PASSWORD={password}\nSCWEET_USERNAME={username}\nHTTP_PROXY={http_proxy}\n"
    # Check if the .env file exists, if not create it
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(content)
        try:
            os.chmod(
                ".env", 0o600
            )  # Set file permissions to rw for the owner only
        except Exception as e:
            logging.info("Error: ", e, " - could not chmod .env, passing...")
        logging.info("write_env: .env file created.")
    else:
        with open(".env", "w") as f:
            f.write(content)
        logging.info("write_env: .env file updated.")


def clear_env():
    # Define the content
    content = (
        f"SCWEET_EMAIL=\nSCWEET_PASSWORD=\nSCWEET_USERNAME=\nHTTP_PROXY=\n"
    )
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(content)
        try:
            os.chmod(
                ".env", 0o600
            )  # Set file permissions to rw for the owner only
        except Exception as e:
            logging.info("Error: ", e, " - could not chmod .env, passing...")
        logging.info("clear_env: .env file created & cleared.")
    else:
        with open(".env", "w") as f:
            f.write(content)
        logging.info("clear_env: .env file cleared.")


def setup_arguments() -> argparse.Namespace:
    def batch_size_type(value):
        ivalue = int(value)
        if ivalue < 5 or ivalue > 200:
            raise argparse.ArgumentTypeError(
                f"custom_batch_size must be between 5 and 200 (got {ivalue})"
            )
        return ivalue

    def validate_module_spec(spec: str) -> str:
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*=https?://github\.com/[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+$"
        if not re.match(pattern, spec):
            raise argparse.ArgumentTypeError(
                f"Invalid module specification: {spec}. "
                "Expecting: module_name=https://github.com/user/repo"
            )

        return spec

    def validate_quota_spec(quota_spec: str) -> dict:
        try:
            domain, quota = quota_spec.split("=")
            quota = int(quota)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid quota specification '{quota_spec}', "
                "quota spec must be in the form 'domain=quota', e.g. 'domain=5000'"
            )
        return {domain: quota}

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--main_address", help="Main wallet", type=str, required=True
    )
    parser.add_argument(
        "--twitter_username", help="Twitter username", type=str
    )
    parser.add_argument(
        "--twitter_password", help="Twitter password", type=str
    )
    parser.add_argument("--twitter_email", help="Twitter email", type=str)
    parser.add_argument(
        "--http_proxy", help="Twitter Selenium PROXY", type=str
    )
    parser.add_argument(
        "-mo",
        "--module_overwrite",
        default=[],
        type=validate_module_spec,
        action="append",  # allow reuse of the option in the same run
        help="Overwrite a sub-module (domain=repository_url)",
    )
    parser.add_argument(
        "--only", type=str, help="Comma-separated list of values", default=""
    )
    parser.add_argument(
        "-qo",
        "--quota",
        default=[],
        type=validate_quota_spec,
        action="append",  # allow reuse of the option in the same run
        help="quota a domain per 24h (domain=amount)",
    )

    parser.add_argument(
        "-ntfy",
        "--ntfy",
        default="",
        type=str,
        help="Provides notification using a ntfy.sh topic",
    )

    def parse_list(s):
        try:
            return int(s)
        except ValueError:
            raise argparse.ArgumentTypeError(
                "Invalid list format. Use comma-separated integers."
            )

    parser.add_argument(
        "-na",
        "--notify_at",
        type=parse_list,
        action="append",
        help="List of integers",
        default=[],
    )

    parser.add_argument(
        "-d",
        "--debug",
        help="Set verbosity level of logs to DEBUG",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "--web", type=bool, help="Experimental web interface for debugging"
    )
    parser.add_argument(
        "--custom_batch_size",
        type=batch_size_type,
        help="Custom batch size (between 5 and 200).",
    )
    args = parser.parse_args()

    # Check that either all or none of Twitter arguments are provided
    args_list = [
        args.twitter_username,
        args.twitter_password,
        args.twitter_email,
    ]
    if (
        args.twitter_username is not None
        and args.twitter_password is not None
        and args.twitter_email is not None
    ):
        logging.info(
            "[Init] Twitter login arguments detected: selecting auth-based scraping."
        )
        http_proxy = ""
        if args.http_proxy is not None:
            http_proxy = args.http_proxy
            logging.info("[Init] Selecting Provided Selenium HTTP Proxy")
        write_env(
            email=args.twitter_email,
            password=args.twitter_password,
            username=args.twitter_username,
            http_proxy=http_proxy,
        )
    elif args_list.count(None) in [1, 2]:
        parser.error(
            "--twitter_username, --twitter_password, and --twitter_email must be given together"
        )
    else:
        logging.info(
            "[Init] No login arguments detected: using login-less scraping"
        )
        clear_env()

    command_line_arguments: argparse.Namespace = parser.parse_args()
    if len(command_line_arguments.notify_at) == 0:
        command_line_arguments.notify_at = [12, 19]

    return command_line_arguments
