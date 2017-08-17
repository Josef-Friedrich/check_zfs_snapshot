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

@test "execute: check_zfs_snapshot -d ok_dataset -c 1 -w 2" {
	run ./check_zfs_snapshot -d ok_dataset -c 1 -w 2
	[ "$status" -eq 3 ]
	[ "${lines[0]}" = '-w INTERVAL_WARNING must be smaller than -c INTERVAL_CRITICAL' ]
}

@test "execute: check_zfs_snapshot -d ok_dataset" {
	run ./check_zfs_snapshot -d ok_dataset
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = 'OK: Last snapshot for dataset “ok_dataset” was created on 2017-08-16T22:15:37Z | last_ago=6328 warning=86400 critical=259200 snapshot_count=3' ]
}

@test "execute: check_zfs_snapshot -d warning_dataset" {
	run ./check_zfs_snapshot -d warning_dataset
	[ "$status" -eq 1 ]
	[ "${lines[0]}" = 'WARNING: Last snapshot for dataset “warning_dataset” was created on 2017-08-16T00:01:04Z | last_ago=86401 warning=86400 critical=259200 snapshot_count=2' ]
}

@test "execute: check_zfs_snapshot -d critical_dataset" {
	run ./check_zfs_snapshot -d critical_dataset
	[ "$status" -eq 2 ]
	[ "${lines[0]}" = 'CRITICAL: Last snapshot for dataset “critical_dataset” was created on 2016-07-23T13:31:50Z | last_ago=33647355 warning=86400 critical=259200 snapshot_count=1' ]
}

@test "function _get_last_snapshot" {
	source_exec ./check_zfs_snapshot
	[ $(_get_last_snapshot ok_dataset) -eq 1502914537 ]
}

@test "function _count_snapshots ok_dataset" {
	source_exec ./check_zfs_snapshot
	[ $(_count_snapshots ok_dataset) -eq 3 ]
}

@test "function _count_snapshots warning_dataset" {
	source_exec ./check_zfs_snapshot
	[ $(_count_snapshots warning_dataset) -eq 2 ]
}

@test "function _count_snapshots critical_dataset" {
	source_exec ./check_zfs_snapshot
	[ $(_count_snapshots critical_dataset) -eq 1 ]
}

@test "default variables" {
	source_exec ./check_zfs_snapshot

	[ "$STATE_OK" -eq  0 ]
	[ "$STATE_WARNING" -eq  1 ]
	[ "$STATE_CRITICAL" -eq  2 ]
	[ "$STATE_UNKNOWN" -eq  3 ]
}
