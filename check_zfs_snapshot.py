#! /usr/bin/env python3

import argparse
from nagiosplugin.runtime import guarded
from typing import cast


class OptionContainer:
    pass


opts: OptionContainer = OptionContainer()


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
        help="Show the version number.",
    )

    parser.add_argument(
        "-w",
        "--warning",
        help="Interval in seconds for warning state. Must be lower than -c",
    )

    return parser


# @guarded(verbose=0)
def main():
    pass
    global opts
    opts = cast(OptionContainer, get_argparser().parse_args())


if __name__ == "__main__":
    main()
