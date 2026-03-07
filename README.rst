.. image:: http://img.shields.io/pypi/v/check-zfs-snapshot.svg
    :target: https://pypi.org/project/check-zfs-snapshot
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/check_zfs_snapshot/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/check_zfs_snapshot/actions/workflows/tests.yml
    :alt: Tests

Note: This monitoring plugin is written in Python from version 3 onwards.
Earlier versions of this plugin were written in shell script. The latest version
of the shell script can be retrieved via the `git history
<https://github.com/Josef-Friedrich/check_zfs_snapshot/tree/e666f8d2877a194713ca75fe4a24aba4fde6a0f4>`__.

Command line interface
----------------------

:: 

    usage: check_zfs_snapshot [-h] [-V] [-v] [-d DATASET] [-w TIMESPAN]
                              [-c TIMESPAN] [--no-performance-data]

    version 2.1.0
    Licensed under the MIT.
    Repository: https://github.com/Josef-Friedrich/check_zfs_snapshot.
    Copyright (c) 2016-2026 Josef Friedrich <josef@friedrich.rocks>

    A monitoring plugin that checks how long ago the last snapshot of ZFS datasets was created.

    options:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      -v, --verbose         Increase the output verbosity.
      -d, --dataset DATASET
                            The ZFS dataset (filesystem) to check.
      -w, --warning TIMESPAN
                            Interval in seconds for warning state. See timespan
                            format specification below. Must be lower than -c
      -c, --critical TIMESPAN
                            Interval in seconds for critical state. See timespan
                            format specification below.
      --no-performance-data
                            Do not attach any performance data to the plugin output.

    Performance data:
     - dataset: last snapshot (timespan in sec)
        The time interval, in seconds, from the present moment until the last snapshot.
     - dataset: last snapshot (timestamp)
        The UNIX timestamp of the last snapshot.
     - dataset: snapshot count
        The number of snapshots of the dataset.

    Timespan format
    ---------------

    If no time unit is specified, generally seconds are assumed. The following time
    units are understood:

    - years, year, y (defined as 365.25 days)
    - months, month, M (defined as 30.44 days)
    - weeks, week, w
    - days, day, d
    - hours, hour, hr, h
    - minutes, minute, min, m
    - seconds, second, sec, s
    - milliseconds, millisecond, msec, ms
    - microseconds,  microsecond, usec, μs, μ, us

    The following are valid examples of timespan specifications:

    - `1`
    - `1.23`
    - `2.345s`
    - `3min 45.234s`
    - `34min`
    - `2 months 8 days`
    - `1h30m`

Project pages
-------------

* https://github.com/Josef-Friedrich/check_zfs_snapshot
* https://exchange.icinga.com/joseffriedrich/check_zfs_snapshot
* https://exchange.nagios.org/directory/Plugins/System-Metrics/File-System/check_zfs_snapshot/details
