#! /usr/bin/env python3

import argparse
import logging
from typing import cast

# from nagiosplugin.runtime import guarded

__version__: str = "1.2"


class OptionContainer:
    pass


opts: OptionContainer = OptionContainer()


class Logger:
    """A wrapper around the Python logging module with 3 debug logging levels.

    1. ``-d``: info
    2. ``-dd``: debug
    3. ``-ddd``: verbose
    """

    __logger: logging.Logger

    __BLUE = "\x1b[0;34m"
    __PURPLE = "\x1b[0;35m"
    __CYAN = "\x1b[0;36m"
    __RESET = "\x1b[0m"

    __INFO = logging.INFO
    __DEBUG = logging.DEBUG
    __VERBOSE = 5

    def __init__(self) -> None:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logging.basicConfig(handlers=[handler])
        self.__logger = logging.getLogger(__name__)

    def set_level(self, level: int) -> None:
        # NOTSET=0
        # custom level: VERBOSE=5
        # DEBUG=10
        # INFO=20
        # WARN=30
        # ERROR=40
        # CRITICAL=50
        if level == 1:
            self.__logger.setLevel(logging.INFO)
        elif level == 2:
            self.__logger.setLevel(logging.DEBUG)
        elif level > 2:
            self.__logger.setLevel(5)

    def __log(self, level: int, color: str, msg: str, *args: object) -> None:
        a: list[str] = []
        for arg in args:
            a.append(color + str(arg) + self.__RESET)
        self.__logger.log(level, msg, *a)

    def info(self, msg: str, *args: object) -> None:
        """Log on debug level ``1``: ``-d``.

        :param msg: A message format string. Note that this means that you can
            use keywords in the format string, together with a single
            dictionary argument. No ``%`` formatting operation is performed on
            ``msg`` when no args are supplied.
        :param args: The arguments which are merged into ``msg`` using the
            string formatting operator.
        """
        self.__log(self.__INFO, self.__BLUE, msg, *args)

    def debug(self, msg: str, *args: object) -> None:
        """Log on debug level ``2``: ``-dd``.

        :param msg: A message format string. Note that this means that you can
            use keywords in the format string, together with a single
            dictionary argument. No ``%`` formatting operation is performed on
            ``msg`` when no args are supplied.
        :param args: The arguments which are merged into ``msg`` using the
            string formatting operator.
        """
        self.__log(self.__DEBUG, self.__PURPLE, msg, *args)

    def verbose(self, msg: str, *args: object) -> None:
        """Log on debug level ``3``: ``-ddd``

        :param msg: A message format string. Note that this means that you can
            use keywords in the format string, together with a single
            dictionary argument. No ``%`` formatting operation is performed on
            ``msg`` when no args are supplied.
        :param args: The arguments which are merged into ``msg`` using the
            string formatting operator.
        """
        self.__log(self.__VERBOSE, self.__CYAN, msg, *args)

    def show_levels(self) -> None:
        msg = "log level %s (%s): %s"
        self.info(msg, 1, "info", "-d")
        self.debug(msg, 2, "debug", "-dd")
        self.verbose(msg, 3, "verbose", "-ddd")


logger = Logger()


def get_argparser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="check_zfs_snapshot",  # To get the right command name in the README.
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog, width=80
        ),  # noqa: E501
        description="Copyright (c) 2016-22 Josef Friedrich <josef@friedrich.rocks>\n"
        "\n"
        "Monitoring plugin to check how long ago the last snapshot of a ZFS dataset was created.\n",  # noqa: E501
        epilog="Performance data:\n"
        " - last_ago\n"
        "    Time interval in seconds for last snapshot.\n"
        " - warning\n"
        "    Interval in seconds.\n"
        " - critical\n"
        "    Interval in seconds.\n"
        " - snapshot_count\n"
        "    How many snapshot exists in the given dataset and all child\n"
        "    datasets exists.\n",
    )

    parser.add_argument(
        "-c",
        "--critical",
        help="Interval in seconds for critical state.",
    )

    parser.add_argument(
        "-d",
        "--dataset",
        help="The ZFS dataset to check.",
    )

    parser.add_argument(
        "-s",
        "--short-description",
        help="Show a short description of the command.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {}".format(__version__),
    )

    parser.add_argument(
        "-w",
        "--warning",
        help="Interval in seconds for warning state. Must be lower than -c",
    )

    parser.add_argument(
        "-D",
        "--debug",
        action="count",
        default=0,
        help="Increase debug verbosity (use up to 3 times): -D: info -DD: debug. -DDD verbose",
    )

    return parser


# @guarded(verbose=0)
def main():
    global opts
    opts = cast(OptionContainer, get_argparser().parse_args())
    print(opts)


if __name__ == "__main__":
    main()
