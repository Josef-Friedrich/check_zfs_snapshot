#!/usr/bin/env bats

setup() {
	. ./test/lib/test-helper.sh
	mock_path test/bin
}

@test "execute: check_zfs_snapshot" {
	skip
	run ./check_zfs_snapshot
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = "'' is no ZFS dataset!" ]
}

@test "execute: check_zfs_snapshot -h" {
	run ./check_zfs_snapshot -h
	[ "$status" -eq 0 ]
}

@test "execute: check_zfs_snapshot -c 2 -w 1" {
	skip
	run ./check_zfs_snapshot -d dataset -c 2 -w 1
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = '-w INTERVAL_WARNING must be smaller than -c INTERVAL_CRITICAL' ]
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

@test "function _get_zpool" {
	source_exec ./check_zfs_snapshot
	[ "$(_get_zpool)" = data ]
}
