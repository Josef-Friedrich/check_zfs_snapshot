#!/usr/bin/env bat

setup() {
	. ./test/test-helper.sh
	mock_path $(pwd)/test/bin
}

@test "execute: check_zfs_snapshot" {
	run ./check_zfs_snapshot
	[ "$status" -eq 3 ]
}
