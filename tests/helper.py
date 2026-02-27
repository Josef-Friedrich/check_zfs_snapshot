from __future__ import annotations

import io
import subprocess
import typing
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from freezegun import freeze_time
from mplugin.testing import MockResult

import check_zfs_snapshot


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["check_zfs_snapshot"] + args,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def execute_main(
    argv: list[str] = ["check_zfs_snapshot"],
    time: str = "2017-08-17 00:01:05",
) -> MockResult:
    def perform_subprocess_output(args: list[str], **kwargs: typing.Any) -> str:
        command: str = " ".join(args)

        if command == "zfs list -H -t snapshot":
            return """critical_dataset@zfs-auto-snap_daily-2017-08-01-2128           0      -  11,1G  -
warning_dataset@zfs-auto-snap_daily-2017-08-05-1916        198K      -  11,1G  -
warning_dataset@zfs-auto-snap_daily-2017-08-06-0945        221K      -  11,1G  -
ok_dataset@zfs-auto-snap_daily-2017-08-07-1835           0      -  11,1G  -
ok_dataset@zfs-auto-snap_weekly-2017-08-07-1835          0      -  11,1G  -
ok_dataset@zfs-auto-snap_daily-2017-08-08-2009        221K      -  11,1G  -
"""

        # 1502914537
        elif command == "zfs get creation -H -p -r -o value -t snapshot ok_dataset":
            return """1469127414
1469273510
1502914518
1502914537
1469127414
1469273510
"""

        # 1502834464
        elif (
            command == "zfs get creation -H -p -r -o value -t snapshot warning_dataset"
        ):
            return """1468255906
1469127414
1502834464
"""

        # 1469273510
        elif (
            command == "zfs get creation -H -p -r -o value -t snapshot warning_dataset"
        ):
            return """1468255906
1469127414
1469273510
"""

        elif command == "zfs list -H":
            return """ok_dataset	7.82T	2.62T	67.7G	/data/ok_dataset
warning_dataset	593G	2.62T	40.6G	/data/warning_dataset
critical_dataset	1.67T	2.62T	46.7G	/data/critical_dataset
"""

        return ""

    if not argv or argv[0] != "check_zfs_snapshot":
        argv.insert(0, "check_zfs_snapshot")

    file_stdout: io.StringIO = io.StringIO()
    file_stderr: io.StringIO = io.StringIO()

    with (
        mock.patch("sys.exit") as sys_exit,
        mock.patch(
            "check_zfs_snapshot.subprocess.check_output",
            side_effect=perform_subprocess_output,
        ),
        mock.patch("sys.argv", argv),
        freeze_time(time),
        redirect_stdout(file_stdout),
        redirect_stderr(file_stderr),
    ):
        check_zfs_snapshot.main()
        check_zfs_snapshot.reset()

    return MockResult(
        sys_exit_mock=sys_exit,
        stdout=file_stdout,
        stderr=file_stderr,
    )
