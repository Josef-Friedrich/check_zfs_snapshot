# check_zfs_snapshot

Note: The monitoring plugin is currently being rewritten from
Shell
([check_zfs_snapshot](https://github.com/Josef-Friedrich/check_zfs_snapshot/blob/master/check_zfs_snapshot)) to
Python
([check_zfs_snapshot.py](https://github.com/Josef-Friedrich/check_zfs_snapshot/blob/master/check_zfs_snapshot.py)). Use the Shell version until further notice.

## Summary / Short description

> Monitoring plugin to check how long ago the last snapshot of a ZFS dataset was created.

## Usage

```
check_zfs_snapshot v1.2
Copyright (c) 2016-2018 Josef Friedrich <josef@friedrich.rocks>

Monitoring plugin to check how long ago the last snapshot of a ZFS dataset was created.


Usage: check_zfs_snapshot <options>

Options:
 -c, --critical=OPT_CRITICAL
    Interval in seconds for critical state.
 -d, --dataset=OPT_DATASET
    The ZFS dataset to check.
 -h, --help
    Show this help.
 -s, --short-description
    Show a short description of the command.
 -v, --version
    Show the version number.
 -w, --warning=OPT_WARNING
    Interval in seconds for warning state. Must be lower than -c

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

```

## Project pages

* https://github.com/Josef-Friedrich/check_zfs_snapshot
* https://exchange.icinga.com/joseffriedrich/check_zfs_snapshot
* https://exchange.nagios.org/directory/Plugins/System-Metrics/File-System/check_zfs_snapshot/details

## Testing

```
make test
```
