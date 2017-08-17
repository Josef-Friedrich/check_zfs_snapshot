[![Build Status](https://travis-ci.org/JosefFriedrich-shell/check_zfs_snapshot.svg?branch=master)](https://travis-ci.org/JosefFriedrich-shell/check_zfs_snapshot)

# check_zfs_snapshot

## Usage

```
check_zfs_snapshot
Copyright (c) 2016 Josef Friedrich <josef@friedrich.rocks>

Checks how long ago the last snapshot of a ZFS dataset was created.


Usage: check_zfs_snapshot <options>

Options:
  -c INTERVAL_CRITICAL
    Interval in seconds for critical state.
  -d DATASET
    The ZFS dataset to check.
  -h
    Show this help.
  -w INTERVAL_WARNING
    Interval in seconds for warning state. Must be lower than -c.
```

## Testing

```
make test
```
