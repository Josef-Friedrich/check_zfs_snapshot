#!/usr/bin/env bats

setup() {
	. ./test/lib/test-helper.sh
	mock_path test/bin
	source_exec ./check_zfs_snapshot
}

@test "function _get_last_snapshot" {
	[ $(_get_last_snapshot ok_dataset) -eq 1502914537 ]
}

@test "function _snapshot_count ok_dataset" {
	[ $(_snapshot_count ok_dataset) -eq 3 ]
}

@test "function _snapshot_count warning_dataset" {
	[ $(_snapshot_count warning_dataset) -eq 2 ]
}

@test "function _snapshot_count critical_dataset" {
	[ $(_snapshot_count critical_dataset) -eq 1 ]
}

@test "default variables" {
	[ "$STATE_OK" -eq  0 ]
	[ "$STATE_WARNING" -eq  1 ]
	[ "$STATE_CRITICAL" -eq  2 ]
	[ "$STATE_UNKNOWN" -eq  3 ]
}

@test "function _getopts --warning=69" {
	_getopts --warning=69
	[ "$INTERVAL_WARNING" -eq  69 ]
}
