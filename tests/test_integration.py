from tests.helper import execute_main as main


def test_first_ok_zpool() -> None:
    result = main(["--dataset", "ok_dataset"])
    assert result.exitcode == 0
    assert result.stdout
    assert (
        "ZFS_SNAPSHOT OK | 'ok_dataset: last_snapshot_timespan'=13528s;86400;259200 'ok_dataset: last_snapshot_timestamp'=1502914537;1502841665;1502668865 'ok_dataset: snapshot_count'=3"
        == result.first_line
    )


def test_all_datasets() -> None:
    result = main([])
    assert result.exitcode == 2
    assert result.stdout
    assert (
        "ZFS_SNAPSHOT CRITICAL - Time span 1502928065 > 259200 | 'critical_dataset: last_snapshot_timespan'=1502928065s;86400;259200 'critical_dataset: last_snapshot_timestamp'=0;1502841665;1502668865 'critical_dataset: snapshot_count'=1 'ok_dataset: last_snapshot_timespan'=13528s;86400;259200 'ok_dataset: last_snapshot_timestamp'=1502914537;1502841665;1502668865 'ok_dataset: snapshot_count'=3 'warning_dataset: last_snapshot_timespan'=93601s;86400;259200 'warning_dataset: last_snapshot_timestamp'=1502834464;1502841665;1502668865 'warning_dataset: snapshot_count'=2"
        == result.first_line
    )


# @test "execute: check_zfs_snapshot -h" {
# 	run ./check_zfs_snapshot -h
# 	[ "$status" -eq 0 ]
# 	[ "${lines[0]}" = "check_zfs_snapshot v$VERSION" ]
# }

# @test "execute: check_zfs_snapshot --help" {
# 	run ./check_zfs_snapshot --help
# 	[ "$status" -eq 0 ]
# 	[ "${lines[0]}" = "check_zfs_snapshot v$VERSION" ]
# }

# @test "execute: check_zfs_snapshot -s" {
# 	run ./check_zfs_snapshot -s
# 	[ "$status" -eq 0 ]
# 	[ "${lines[0]}" = 'Monitoring plugin to check how long ago the last snapshot of a ZFS dataset was created.' ]
# }

# @test "execute: check_zfs_snapshot --short-description" {
# 	run ./check_zfs_snapshot --short-description
# 	[ "$status" -eq 0 ]
# 	[ "${lines[0]}" = 'Monitoring plugin to check how long ago the last snapshot of a ZFS dataset was created.' ]
# }

# @test "execute: check_zfs_snapshot -d ok_dataset -c 1 -w 2" {
# 	run ./check_zfs_snapshot -d ok_dataset -c 1 -w 2
# 	[ "$status" -eq 3 ]
# 	[ "${lines[0]}" = '-w OPT_WARNING must be smaller than -c OPT_CRITICAL' ]
# }

# @test "execute: check_zfs_snapshot --dataset=ok_dataset --critical=1 --warning=2" {
# 	run ./check_zfs_snapshot --dataset=ok_dataset --critical=1 --warning=2
# 	[ "$status" -eq 3 ]
# 	[ "${lines[0]}" = '-w OPT_WARNING must be smaller than -c OPT_CRITICAL' ]
# }

# @test "execute: check_zfs_snapshot -d ok_dataset" {
# 	run ./check_zfs_snapshot -d ok_dataset
# 	[ "$status" -eq 0 ]
# 	[ "${lines[0]}" = "OK: Last snapshot for dataset 'ok_dataset' was created on 2017-08-16.22:15:37 | last_ago=6328 warning=86400 critical=259200 snapshot_count=3" ]
# }

# @test "execute: check_zfs_snapshot -d warning_dataset" {
# 	run ./check_zfs_snapshot -d warning_dataset
# 	[ "$status" -eq 1 ]
# 	[ "${lines[0]}" = "WARNING: Last snapshot for dataset 'warning_dataset' was created on 2017-08-16.00:01:04 | last_ago=86401 warning=86400 critical=259200 snapshot_count=2" ]
# }

# @test "execute: check_zfs_snapshot -d critical_dataset" {
# 	run ./check_zfs_snapshot -d critical_dataset
# 	[ "$status" -eq 2 ]
# 	[ "${lines[0]}" = "CRITICAL: Last snapshot for dataset 'critical_dataset' was created on 2016-07-23.13:31:50 | last_ago=33647355 warning=86400 critical=259200 snapshot_count=1" ]
# }
