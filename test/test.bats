#!/usr/bin/env bats

setup() {
	. ./test/lib/test-helper.sh
	mock_path bin
}

@test "execute: check_zfs_snapshot" {
	run ./check_zfs_snapshot
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = "'' is no ZFS dataset!" ]
}

@test "execute: check_zfs_snapshot -h" {
	run ./check_zfs_snapshot -h
	[ "$status" -eq 0 ]
}

@test "execute: check_zfs_snapshot -c 2 -w 1" {
	run ./check_zfs_snapshot -d dataset -c 2 -w 1
	[ "$status" -eq 3 ]
	# [ "${lines[0]}" = '-w INTERVAL_WARNING must be smaller than -c INTERVAL_CRITICAL' ]
}

@test "execute: check_zfs_snapshot -d unkown_dataset" {
	run ./check_zfs_snapshot -d unkown_dataset
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = "'unkown_dataset' is no ZFS dataset!" ]
}
