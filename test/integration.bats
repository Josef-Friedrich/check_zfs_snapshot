#!/usr/bin/env bats

setup() {
	. ./test/lib/test-helper.sh
	mock_path test/bin
	source_exec ./check_zfs_snapshot

}

@test "execute: check_zfs_snapshot" {
	run ./check_zfs_snapshot
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = "Dataset has to be set! Use option -d <dataset>" ]
	[ "${lines[1]}" = "check_zfs_snapshot v1.1" ]
}

@test "execute: check_zfs_snapshot -h" {
	run ./check_zfs_snapshot -h
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "check_zfs_snapshot v$VERSION" ]
}

@test "execute: check_zfs_snapshot --help" {
	run ./check_zfs_snapshot --help
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "check_zfs_snapshot v$VERSION" ]
}

@test "execute: check_zfs_snapshot -s" {
	run ./check_zfs_snapshot -s
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = 'Monitoring plugin to check how long ago the last snapshot of a ZFS dataset was created.' ]
}

@test "execute: check_zfs_snapshot --short-description" {
	run ./check_zfs_snapshot --short-description
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = 'Monitoring plugin to check how long ago the last snapshot of a ZFS dataset was created.' ]
}

@test "execute: check_zfs_snapshot -d ok_dataset -c 1 -w 2" {
	run ./check_zfs_snapshot -d ok_dataset -c 1 -w 2
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = '-w OPT_WARNING must be smaller than -c OPT_CRITICAL' ]
}

@test "execute: check_zfs_snapshot --dataset=ok_dataset --critical=1 --warning=2" {
	run ./check_zfs_snapshot --dataset=ok_dataset --critical=1 --warning=2
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = '-w OPT_WARNING must be smaller than -c OPT_CRITICAL' ]
}

@test "execute: check_zfs_snapshot -d ok_dataset" {
	run ./check_zfs_snapshot -d ok_dataset
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "OK: Last snapshot for dataset 'ok_dataset' was created on 2017-08-16.22:15:37 | last_ago=6328 warning=86400 critical=259200 snapshot_count=3" ]
}

@test "execute: check_zfs_snapshot -d warning_dataset" {
	run ./check_zfs_snapshot -d warning_dataset
	[ "$status" -eq 1 ]
	[ "${lines[0]}" = "WARNING: Last snapshot for dataset 'warning_dataset' was created on 2017-08-16.00:01:04 | last_ago=86401 warning=86400 critical=259200 snapshot_count=2" ]
}

@test "execute: check_zfs_snapshot -d critical_dataset" {
	run ./check_zfs_snapshot -d critical_dataset
	[ "$status" -eq 2 ]
	[ "${lines[0]}" = "CRITICAL: Last snapshot for dataset 'critical_dataset' was created on 2016-07-23.13:31:50 | last_ago=33647355 warning=86400 critical=259200 snapshot_count=1" ]
}
