#! /usr/bin/env python3

import argparse
import datetime
import logging
import subprocess
import typing
from typing import Optional, cast

import nagiosplugin

# from nagiosplugin.runtime import guarded

"""
There's 3 types of datasets in ZFS: a filesystem following POSIX rules, a
volume (zvol) existing as a true block device under /dev, and snapshots
thereof. Datasets are listed, one on each line, by zfs list. By default
snapshots are hidden so use zfs list -t snapshot or zfs list -t all to see
them. When you need to generically refer to a filesystem or volume, you can
call it a dataset. A snapshot could be called "snapshot of a filesystem" or
"snapshot of a volume", but generally we just call them snapshots.

While a clone is a dataset like any other, I wouldn't classify it as a special
type. It's special because it's not created from scratch and initially blank,
but uses a snapshot for its starting data and is how you could work from a
snapshot and be able to write to it (snapshots are strictly read-only). They're
only really special because while they exist the aforementioned snapshot can't
be deleted and the parent/child relationship with that snapshot needs to be
managed.

For reference I would use the ZFS man page itself which says:

    The command configures ZFS datasets within a ZFS storage pool, as described
    in zpool(8). A dataset is identified by a unique path within the ZFS
    namespace. For example: pool/{filesystem,volume,snapshot}


https://www.reddit.com/r/zfs/comments/j9bfh5/new_zfs_trying_to_understand_datasets_vs/

"""

__version__: str = "1.2"


class OptionContainer:
    dataset: Optional[str]
    debug: int
    verbose: int
    warning: int
    critical: int


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
        self.info(msg, 1, "info", "-D")
        self.debug(msg, 2, "debug", "-DD")
        self.verbose(msg, 3, "verbose", "-DDD")


logger = Logger()


def _list_datasets() -> list[str]:
    output = subprocess.check_output(
        [
            "zfs",
            "list",
            # -H  Used for scripting mode.  Do not print headers and separate fields by a single tab instead of arbitrary white space.
            "-H",
        ],
        encoding="utf-8",
    ).splitlines()
    datasets: list[str] = []
    for line in output:
        logger.verbose("Output from %s: %s", "zfs list", line)
        datasets.append(line.split("\t")[0])
    return datasets


_all_snapshots_output: typing.Optional[list[str]] = None


def _count_snapshots(dataset: str) -> int:
    # data/video@zfs-auto-snap_hourly-2026-01-31-0900                       0B      -   255G  -
    # data/video@zfs-auto-snap_frequent-2026-01-31-0900                     0B      -   255G  -
    # data/video@zfs-auto-snap_frequent-2026-01-31-1032                     0B      -   255G  -
    # data/video@zfs-auto-snap_hourly-2026-01-31-1032                       0B      -   255G  -
    # data/video@zfs-auto-snap_frequent-2026-01-31-1045                     0B      -   255G  -
    global _all_snapshots_output
    if _all_snapshots_output is None:
        _all_snapshots_output = (
            subprocess.check_output(
                [
                    "zfs",
                    "list",
                    # -H  Used for scripting mode. Do not print headers and separate fields by a single tab instead of arbitrary white space.
                    "-H",
                    # -t type A comma-separated list of types to display, where type is one of filesystem, snapshot, volume, bookmark, or all.
                    "-t",
                    "snapshot",
                ],
                encoding="utf-8",
            )
            .strip()
            .splitlines()
        )
    counter = 0
    for line in _all_snapshots_output:
        logger.verbose("Output from %s: %s", "zfs list -t snapshot", line)
        snapshot = line.split("\t")[0]
        if snapshot.startswith(f"{dataset}@"):
            counter += 1
    return counter


# scope: snapshot_count #######################################################


class SnapshotCountResource(nagiosplugin.Resource):
    name = "snapshot_count"

    dataset: str

    def __init__(self, dataset: str) -> None:
        self.dataset = dataset

    def probe(self) -> nagiosplugin.Metric:
        return nagiosplugin.Metric(
            "snapshot_count__" + self.dataset, _count_snapshots(self.dataset)
        )


class PerformanceDataContext(nagiosplugin.Context):
    def __init__(self) -> None:
        super().__init__("snapshot_count")

    def performance(
        self, metric: nagiosplugin.Metric, resource: nagiosplugin.Resource
    ) -> nagiosplugin.Performance:
        return nagiosplugin.Performance(label=metric.name, value=metric.value)


# scope: last_snapshot ########################################################


class LastSnapshotResource(nagiosplugin.Resource):
    name = "last_snapshot"

    dataset: str

    def __init__(self, dataset: str) -> None:
        self.dataset = dataset

    def probe(self) -> nagiosplugin.Metric:
        output = subprocess.check_output(
            [
                "zfs",
                "get",
                # -H Display  output in a form more easily parsed by scripts. Any headers are omitted, and fields are explicitly separated by a single tab instead of an arbitrary amount of space.
                "-H",
                # -p Display numbers in parsable (exact) values.
                "-p",
                # -r Recursively display properties for any children.
                "-r",
                # -o field A comma-separated list of columns to display, defaults to name,property,value,source.
                "-o",
                "value",
                # -t type A comma-separated list of types to display, where type is one of filesystem, snapshot, volume, bookmark, or all.
                "-t",
                "snapshot",
                "creation",
                self.dataset,
            ],
            encoding="utf-8",
        ).splitlines()
        last = 0
        for line in output:
            logger.verbose("Output from %s: %s", "zfs get creation", line)
            timestamp = int(line)
            if timestamp > last:
                last = timestamp
        return nagiosplugin.Metric("last_snapshot__" + self.dataset, last)


class LastSnapshotContext(nagiosplugin.Context):
    def __init__(self) -> None:
        super().__init__("last_snapshot")

    def performance(
        self, metric: nagiosplugin.Metric, resource: nagiosplugin.Resource
    ) -> nagiosplugin.Performance:
        return nagiosplugin.Performance(label=metric.name, value=metric.value)

    def evaluate(
        self, metric: nagiosplugin.Metric, resource: nagiosplugin.Resource
    ) -> nagiosplugin.Result:
        last_snapshot: int = metric.value
        now: int = int(datetime.datetime.now().timestamp())
        time_span: int = now - last_snapshot
        if time_span > opts.critical:
            return self.result_cls(
                nagiosplugin.Critical,
                hint=f"now ({now}) - last_snapshot ({last_snapshot}) = {time_span} > {opts.critical}",
                metric=metric,
            )
        if time_span > opts.warning:
            return self.result_cls(
                nagiosplugin.Warn,
                hint=f"now ({now}) - last_snapshot ({last_snapshot}) = {time_span} > {opts.warning}",
                metric=metric,
            )
        return self.result_cls(
            nagiosplugin.Ok,
            hint=f"now ({now}) - last_snapshot ({last_snapshot}) = {time_span} < {opts.warning}",
            metric=metric,
        )


def get_argparser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="check_zfs_snapshot",  # To get the right command name in the README.
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog, width=80
        ),  # noqa: E501
        description="Copyright (c) 2016-2026 Josef Friedrich <josef@friedrich.rocks>\n"
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
        "-V",
        "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (use up to 3 times).",
    )

    parser.add_argument(
        "-c",
        "--critical",
        # 3 days:
        default=259200,
        type=int,
        metavar="SECONDS",
        help="Interval in seconds for critical state.",
    )

    parser.add_argument(
        "-d",
        "--dataset",
        help="The ZFS dataset (filesystem) to check.",
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
        # 1 day:
        default=86400,
        type=int,
        metavar="SECONDS",
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
def main() -> None:
    global opts
    opts = cast(OptionContainer, get_argparser().parse_args())

    logger.set_level(opts.debug)
    logger.show_levels()
    logger.verbose("Normalized argparse options: %s", opts)

    if opts.warning > opts.critical:
        raise ValueError(
            f"-w SECONDS must be smaller than -c SECONDS. -w {opts.warning} > -c {opts.critical}"
        )

    datasets = _list_datasets()

    checks: list[typing.Union[nagiosplugin.Resource, nagiosplugin.Context]] = [
        LastSnapshotContext(),
        PerformanceDataContext(),
    ]

    if opts.dataset is not None:
        if opts.dataset not in datasets:
            raise ValueError(f"-d {opts.dataset} is not in {datasets}")
        checks.append(SnapshotCountResource(opts.dataset))
        checks.append(LastSnapshotResource(opts.dataset))
    else:
        for dataset in datasets:
            checks.append(SnapshotCountResource(dataset))
            checks.append(LastSnapshotResource(dataset))

    check: nagiosplugin.Check = nagiosplugin.Check(*checks)
    check.name = "zfs_snapshot"
    check.main(opts.verbose)


if __name__ == "__main__":
    main()
