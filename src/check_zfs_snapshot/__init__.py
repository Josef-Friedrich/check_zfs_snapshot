#! /usr/bin/env python3

import argparse
import subprocess
import typing
from datetime import datetime
from importlib import metadata
from typing import Optional, cast

import mplugin
from mplugin import log

"""
There are three types of datasets in ZFS:

1. a file system that follows POSIX rules
2. a volume (zvol) that exists as a true block device under /dev,
3. and snapshots thereof.

Datasets are listed one per line by the ``zfs list`` command. By default,
snapshots are hidden, so use ``zfs list -t snapshot`` or ``zfs list -t all`` to
view them. You can call a filesystem or volume a dataset when you need to refer
to it generically. A snapshot could be called "snapshot of a file system" or
"snapshot of a volume," but we generally just call them snapshots.

A clone is a dataset like any other; however, I wouldn't classify it as a
special type. It's special because it's not created from scratch as an initial
blank dataset, but rather uses a snapshot for its starting data. This allows
you to work from a snapshot and write to it, whereas snapshots are strictly
read-only. Clones are only special in that, while they exist, the
aforementioned snapshot cannot be deleted, and the parent/child relationship
with that snapshot needs to be managed.

For reference I would use the ZFS man page itself which says:

    The command configures ZFS datasets within a ZFS storage pool, as described
    in zpool(8). A dataset is identified by a unique path within the ZFS
    namespace. For example: pool/{filesystem,volume,snapshot}

https://www.reddit.com/r/zfs/comments/j9bfh5/new_zfs_trying_to_understand_datasets_vs/
"""

__version__: str = metadata.version("check_zfs_snapshot")


class OptionContainer:
    dataset: Optional[str]
    verbose: int
    warning: int
    critical: int
    no_performance_data: bool


opts: OptionContainer = OptionContainer()


def get_argparser() -> argparse.ArgumentParser:
    parser = mplugin.setup_argparser(
        name="zfs_snapshot",
        version=__version__,
        license="MIT",
        repository="https://github.com/Josef-Friedrich/check_zfs_snapshot",
        copyright="Copyright (c) 2016-2026 Josef Friedrich <josef@friedrich.rocks>",
        description="A monitoring plugin that checks how long ago the last snapshot of ZFS datasets was created.",
        epilog="Performance data:\n"
        " - dataset: last snapshot (timespan in sec)\n"
        "    The time interval, in seconds, from the present moment until the last snapshot.\n"
        " - dataset: last snapshot (timestamp)\n"
        "    The UNIX timestamp of the last snapshot.\n"
        " - dataset: snapshot count\n"
        "    The number of snapshots of the dataset.\n" + mplugin.TIMESPAN_FORMAT_HELP,
        verbose=True,
    )

    parser.add_argument(
        "-d",
        "--dataset",
        help="The ZFS dataset (filesystem) to check.",
    )

    parser.add_argument(
        "-w",
        "--warning",
        # 1 day:
        default=86400,
        type=mplugin.timespan,
        metavar="TIMESPAN",
        help="Interval in seconds for warning state. See timespan format specification below. Must be lower than -c",
    )

    parser.add_argument(
        "-c",
        "--critical",
        # 3 days:
        default=259200,
        type=mplugin.timespan,
        metavar="TIMESPAN",
        help="Interval in seconds for critical state. See timespan format specification below.",
    )

    parser.add_argument(
        "--no-performance-data",
        action="store_true",
        help="Do not attach any performance data to the plugin output.",
    )

    return parser


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
        log.debug("Output from '%s': %s", "zfs list -H", line)
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
        log.debug("Output from '%s': %s", "zfs list -H -t snapshot", line)
        snapshot = line.split("\t")[0]
        if snapshot.startswith(f"{dataset}@"):
            counter += 1
    return counter


DateTimeSpec = typing.Optional[typing.Union[int, float, datetime]]


class Timespan:
    start: datetime

    end: datetime

    def __init__(
        self,
        start: DateTimeSpec = None,
        end: DateTimeSpec = None,
        timespan_from_now: typing.Optional[typing.Union[int, float]] = None,
    ) -> None:

        if not (start is None and end is None) and timespan_from_now is not None:
            raise ValueError("specify start or end OR timespan_from_now")

        if timespan_from_now is None:
            self.start = Timespan.__normalize(start)
            self.end = Timespan.__normalize(end)
        else:
            self.end = Timespan.__normalize()
            self.start = Timespan.__normalize(self.end.timestamp() - timespan_from_now)

    @property
    def timespan(self) -> float:
        return self.end.timestamp() - self.start.timestamp()

    @staticmethod
    def __normalize(date: DateTimeSpec = None) -> datetime:
        if date is None:
            return datetime.now()
        if isinstance(date, int) or isinstance(date, float):
            return datetime.fromtimestamp(date)
        return date

    def __lt__(self, other: typing.Any) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            return self.timespan < other
        raise ValueError("Unsupported type for __lt__")

    def __le__(self, other: typing.Any) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            return self.timespan <= other
        raise ValueError("Unsupported type for __le__")

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            return self.timespan == other
        raise ValueError("Unsupported type for __eq__")

    def __ne__(self, other: typing.Any) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            return self.timespan != other
        raise ValueError("Unsupported type for __ne__")

    def __ge__(self, other: typing.Any) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            return self.timespan >= other
        raise ValueError("Unsupported type for __ge__")

    def __gt__(self, other: typing.Any) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            return self.timespan > other
        raise ValueError("Unsupported type for __gt__")

    def __float__(self) -> float:
        return self.timespan

    def __int__(self) -> int:
        return round(self.timespan)

    def __str__(self) -> str:
        return f"{self.start.isoformat()} - {self.end.isoformat()}"


# scope: snapshot_count #######################################################


class SnapshotCountResource(mplugin.Resource):
    dataset: str

    def __init__(self, dataset: str) -> None:
        self.dataset = dataset

    def probe(self) -> mplugin.Metric:
        return mplugin.Metric("snapshot_count", _count_snapshots(self.dataset))


class PerformanceDataContext(mplugin.Context):
    def __init__(self) -> None:
        super().__init__("snapshot_count")

    def performance(
        self, metric: mplugin.Metric, resource: mplugin.Resource
    ) -> Optional[mplugin.Performance]:
        if opts.no_performance_data:
            return None
        return mplugin.Performance(
            label=cast(SnapshotCountResource, resource).dataset + ": snapshot count",
            value=metric.value,
        )


# scope: last_snapshot ########################################################


class LastSnapshotResource(mplugin.Resource):
    dataset: str

    def __init__(self, dataset: str) -> None:
        self.dataset = dataset

    def probe(self) -> mplugin.Metric:
        output = subprocess.check_output(
            [
                "zfs",
                "get",
                "creation",
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
                self.dataset,
            ],
            encoding="utf-8",
        ).splitlines()
        last = 0
        for line in output:
            log.debug(
                "Output from '%s': %s",
                "zfs get creation -Hpr -o value -t snapshot " + self.dataset,
                line,
            )
            timestamp = int(line)
            if timestamp > last:
                last = timestamp
        return mplugin.Metric("last_snapshot", Timespan(start=last))


class LastSnapshotContext(mplugin.Context):
    def __init__(self) -> None:
        super().__init__("last_snapshot")

    def evaluate(
        self, metric: mplugin.Metric, resource: mplugin.Resource
    ) -> mplugin.Result:
        timespan: Timespan = metric.value
        dataset: str = cast(LastSnapshotResource, resource).dataset

        hint = f"Last snapshot for dataset '{dataset}' was created on {timespan.start.isoformat()}"

        if timespan >= opts.critical:
            return self.critical(
                hint=hint,
                metric=metric,
            )
        if timespan >= opts.warning:
            return self.warning(
                hint=hint,
                metric=metric,
            )
        return self.ok(
            hint=hint,
            metric=metric,
        )

    def performance(
        self, metric: mplugin.Metric, resource: mplugin.Resource
    ) -> typing.Optional[typing.Generator[mplugin.Performance, typing.Any, None]]:
        if opts.no_performance_data:
            return None
        timespan: Timespan = metric.value

        #  timespan
        yield mplugin.Performance(
            label=cast(LastSnapshotResource, resource).dataset
            + ": "
            + "last snapshot (timespan in sec)",
            value=int(timespan),
            uom="s",
            warn=int(opts.warning),
            crit=int(opts.critical),
        )

        # timestamp
        yield mplugin.Performance(
            label=cast(LastSnapshotResource, resource).dataset
            + ": "
            + "last snapshot (timestamp)",
            value=int(timespan.start.timestamp()),
            warn=int(Timespan(timespan_from_now=opts.warning).start.timestamp()),
            crit=int(Timespan(timespan_from_now=opts.critical).start.timestamp()),
        )
        return None


def reset() -> None:
    """
    Only required for the tests
    """
    global _all_snapshots_output
    _all_snapshots_output = None


@mplugin.guarded(verbose=0)
def main() -> None:
    global opts
    opts = cast(OptionContainer, get_argparser().parse_args())

    if opts.warning > opts.critical:
        raise ValueError(
            f"-w SECONDS must be smaller than -c SECONDS. -w {opts.warning} > -c {opts.critical}"
        )

    datasets = _list_datasets()

    checks: list[typing.Union[mplugin.Resource, mplugin.Context]] = [
        LastSnapshotContext(),
        PerformanceDataContext(),
    ]

    def add_resources(dataset: str) -> None:
        checks.append(SnapshotCountResource(dataset))
        checks.append(LastSnapshotResource(dataset))

    if opts.dataset is not None:
        if opts.dataset not in datasets:
            raise ValueError(f"-d {opts.dataset} is not in {datasets}")
        add_resources(opts.dataset)
    else:
        for dataset in datasets:
            add_resources(dataset)

    check: mplugin.Check = mplugin.Check(*checks)
    check.name = "zfs_snapshot"
    check.main(verbose=opts.verbose)


if __name__ == "__main__":
    main()
