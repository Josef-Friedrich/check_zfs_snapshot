.. image:: http://img.shields.io/pypi/v/check-zfs-snapshot.svg
    :target: https://pypi.org/project/check-zfs-snapshot
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/check_zfs_snapshot/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/check_zfs_snapshot/actions/workflows/tests.yml
    :alt: Tests

Command line interface
----------------------

:: 

    usage: check_zfs_snapshot [-h] [-c CRITICAL] [-d DATASET] [-s SHORT_DESCRIPTION]
                              [-v] [-w WARNING]

    Copyright (c) 2016-22 Josef Friedrich <josef@friedrich.rocks>

    Monitoring plugin to check how long ago the last snapshot of a ZFS dataset was created.

    options:
      -h, --help            show this help message and exit
      -c CRITICAL, --critical CRITICAL
                            Interval in seconds for critical state.
      -d DATASET, --dataset DATASET
                            The ZFS dataset to check.
      -s SHORT_DESCRIPTION, --short-description SHORT_DESCRIPTION
                            Show a short description of the command.
      -v, --version         show program's version number and exit
      -w WARNING, --warning WARNING
                            Interval in seconds for warning state. Must be lower
                            than -c

    Performance data:
     - last_ago
        Time interval in seconds for last snapshot.
     - warning
        Interval in seconds.
     - critical
        Interval in seconds.
     - snapshot_count
        How many snapshot exists in the given dataset and all child
        datasets exists.

