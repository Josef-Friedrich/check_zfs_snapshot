.. image:: http://img.shields.io/pypi/v/check-zfs-snapshot.svg
    :target: https://pypi.org/project/check-zfs-snapshot
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/check_zfs_snapshot/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/check_zfs_snapshot/actions/workflows/tests.yml
    :alt: Tests

Command line interface
----------------------

:: 

    usage: check_zfs_snapshot [-h] [-V] [-v] [-w SECONDS] [-c SECONDS] [-d DATASET]
                              [-D]

    version 2.1.0
    Licensed under the MIT.
    Repository: https://github.com/Josef-Friedrich/check_zfs_snapshot.
    Copyright (c) 2016-2026 Josef Friedrich <josef@friedrich.rocks>

    A monitoring plugin that checks how long ago the last snapshot of ZFS datasets was created.

    options:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      -v, --verbose         Increase output verbosity (use up to 3 times).
      -w, --warning SECONDS
                            Interval in seconds for warning state. Must be lower
                            than -c
      -c, --critical SECONDS
                            Interval in seconds for critical state.
      -d, --dataset DATASET
                            The ZFS dataset (filesystem) to check.
      -D, --debug           Increase debug verbosity (use up to 3 times): -D: info
                            -DD: debug. -DDD verbose

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

Project pages
-------------

* https://github.com/Josef-Friedrich/check_zfs_snapshot
* https://exchange.icinga.com/joseffriedrich/check_zfs_snapshot
* https://exchange.nagios.org/directory/Plugins/System-Metrics/File-System/check_zfs_snapshot/details
