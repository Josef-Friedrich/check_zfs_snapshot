#!/usr/bin/env bats

setup() {
	. ./test/lib/test-helper.sh
	mock_path test/bin
}

@test "execute: check_zfs_snapshot" {
	run ./check_zfs_snapshot
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = "Dataset has to be set! Use option -d <dataset>" ]
}

@test "execute: check_zfs_snapshot -h" {
	run ./check_zfs_snapshot -h
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "check_zfs_snapshot" ]
}

@test "execute: check_zfs_snapshot -d dataset -c 1 -w 2" {
	run ./check_zfs_snapshot -d dataset -c 1 -w 2
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = '-w INTERVAL_WARNING must be smaller than -c INTERVAL_CRITICAL' ]
}

@test "execute: check_zfs_snapshot -d dataset" {
	run ./check_zfs_snapshot -d dataset
	[ "$status" -eq 0 ]
}

@test "execute: check_zfs_snapshot -d unkown_dataset" {
	run ./check_zfs_snapshot -d unkown_dataset
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = "'unkown_dataset' is no ZFS dataset!" ]
}

@test "function _get_last_snapshot" {
	source_exec ./check_zfs_snapshot
	NOW=$(date +%s)
	[ $(_get_last_snapshot dataset) -gt $((NOW - 1000)) ]
}
