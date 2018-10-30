#!/usr/bin/env bats

setup() {
	. ./test/lib/test-helper.sh
	source_exec check_zfs_snapshot
}

##
# date
##

@test "function _now_to_year" {
	result=$(_now_to_year)
	[ "$result" -eq "$(date +%Y)" ]
}

@test "function _date_to_year" {
	result=$(_date_to_year 2016-09-08)
	[ "$result" -eq 2016 ]
}

@test "function _timestamp_to_datetime" {
	result=$(_timestamp_to_datetime 1497601547)
	[ "$result" = "2017-06-16.10:25:47" ]
}

@test "function _now_to_timestamp" {
	result=$(_now_to_timestamp)
	[ "$result" -gt 1533570437 ]
}
