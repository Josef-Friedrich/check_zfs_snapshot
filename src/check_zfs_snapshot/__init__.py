#! /usr/bin/env python3

import argparse
import datetime
import subprocess
import typing
from importlib import metadata
from typing import Optional, cast

import mplugin
from mplugin import log

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

__version__: str = metadata.version("check_zfs_snapshot")


class OptionContainer:
    dataset: Optional[str]
    debug: int
    verbose: int
    warning: int
    critical: int


opts: OptionContainer = OptionContainer()


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
        log.debug("Output from %s: %s", "zfs list", line)
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
        log.debug("Output from %s: %s", "zfs list -t snapshot", line)
        snapshot = line.split("\t")[0]
        if snapshot.startswith(f"{dataset}@"):
            counter += 1
    return counter


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
    ) -> mplugin.Performance:
        return mplugin.Performance(
            label=cast(SnapshotCountResource, resource).dataset + ": " + metric.name,
            value=metric.value,
        )


# scope: last_snapshot ########################################################


class LastSnapshotResource(mplugin.Resource):
    dataset: str

    def __init__(self, dataset: str) -> None:
        self.dataset = dataset

    def probe(self) -> typing.Generator[mplugin.Metric, typing.Any, None]:
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
            log.debug("Output from %s: %s", "zfs get creation", line)
            timestamp = int(line)
            if timestamp > last:
                last = timestamp
        yield mplugin.Metric("last_snapshot_timestamp", last)
        yield mplugin.Metric(
            "last_snapshot_timespan", int(datetime.datetime.now().timestamp()) - last
        )


class LastSnapshotTimespanContext(mplugin.Context):
    def __init__(self) -> None:
        super().__init__("last_snapshot_timespan")

    def performance(
        self, metric: mplugin.Metric, resource: mplugin.Resource
    ) -> mplugin.Performance:
        return mplugin.Performance(
            label=cast(LastSnapshotResource, resource).dataset + ": " + metric.name,
            value=metric.value,
            uom="s",
            warn=opts.warning,
            crit=opts.critical,
        )

    def evaluate(
        self, metric: mplugin.Metric, resource: mplugin.Resource
    ) -> mplugin.Result:
        time_span: int = metric.value
        if time_span > opts.critical:
            return self.critical(
                hint=f"Time span {time_span} > {opts.critical}",
                metric=metric,
            )
        if time_span > opts.warning:
            return self.warning(
                hint=f"Time span {time_span} > {opts.warning}",
                metric=metric,
            )
        return self.ok(
            hint=f"Time span {time_span} < {opts.warning}",
            metric=metric,
        )


class LastSnapshotTimestampContext(mplugin.Context):
    def __init__(self) -> None:
        super().__init__("last_snapshot_timestamp")

    def performance(
        self, metric: mplugin.Metric, resource: mplugin.Resource
    ) -> mplugin.Performance:
        now = datetime.datetime.now().timestamp()
        return mplugin.Performance(
            label=cast(LastSnapshotResource, resource).dataset + ": " + metric.name,
            value=metric.value,
            warn=round(now - opts.warning),
            crit=round(now - opts.critical),
        )


def get_argparser() -> argparse.ArgumentParser:
    parser = mplugin.setup_argparser(
        name="zfs_snapshot",
        version=__version__,
        license="MIT",
        repository="https://github.com/Josef-Friedrich/check_zfs_snapshot",
        copyright="Copyright (c) 2016-2026 Josef Friedrich <josef@friedrich.rocks>",
        description="A monitoring plugin that checks how long ago the last snapshot of ZFS datasets was created.",
        epilog="Performance data:\n"
        " - last_ago\n"
        "    Time interval in seconds for last snapshot.\n"
        " - warning\n"
        "    Interval in seconds.\n"
        " - critical\n"
        "    Interval in seconds.\n"
        " - snapshot_count\n"
        "    How many snapshot exists in the given dataset and all child\n"
        "    datasets exists.\n" + mplugin.TIMESPAN_FORMAT_HELP,
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

    return parser


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
        LastSnapshotTimespanContext(),
        LastSnapshotTimestampContext(),
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
