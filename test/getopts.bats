#!/usr/bin/env bats

setup() {
	. ./test/lib/test-helper.sh
	source_exec check_zfs_snapshot
}

# -c

@test "_getopts -c 123" {
	_getopts -c 123
	[ "$OPT_CRITICAL" -eq 123 ]
}

@test "_getopts -c" {
	run _getopts -c
	[ "$status" -eq 3 ]
}

@test "_getopts --critical=123" {
	_getopts --critical=123
	[ "$OPT_CRITICAL" -eq 123 ]
}

@test "_getopts --critical" {
	run _getopts --critical
	[ "$status" -eq 3 ]
}

# -d

@test "_getopts -d 123" {
	_getopts -d 123
	[ "$OPT_DATASET" -eq 123 ]
}

@test "_getopts -d" {
	run _getopts -d
	[ "$status" -eq 3 ]
}

@test "_getopts --dataset=123" {
	_getopts --dataset=123
	[ "$OPT_DATASET" -eq 123 ]
}

@test "_getopts --dataset" {
	run _getopts --dataset
	[ "$status" -eq 3 ]
}


# -h

@test "_getopts -h" {
	run _getopts -h
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "check_zfs_snapshot v$VERSION" ]
}

@test "_getopts --help" {
	run _getopts --help
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "check_zfs_snapshot v$VERSION" ]
}

@test "_getopts --help=123" {
	run _getopts --help=123
	[ "$status" -eq 4 ]
}

# -s

@test "_getopts -s" {
	run _getopts -s
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "Monitoring plugin to check how long ago the last \
snapshot of a ZFS dataset was created." ]
}

@test "_getopts --short-description" {
	run _getopts --short-description
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "Monitoring plugin to check how long ago the last \
snapshot of a ZFS dataset was created." ]
}

@test "_getopts --short-description=123" {
	run _getopts --short-description=123
	[ "$status" -eq 4 ]
}

# -v

@test "_getopts -v" {
	run _getopts -v
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "$VERSION" ]
}

@test "_getopts --version" {
	run _getopts --version
	[ "$status" -eq 0 ]
	[ "${lines[0]}" = "$VERSION" ]
}

@test "_getopts --version=123" {
	run _getopts --version=123
	[ "$status" -eq 4 ]
}

# -w

@test "_getopts -w 123" {
	_getopts -w 123
	[ "$OPT_WARNING" -eq 123 ]
}

@test "_getopts -w" {
	run _getopts -w
	[ "$status" -eq 3 ]
}

@test "_getopts --warning=123" {
	_getopts --warning=123
	[ "$OPT_WARNING" -eq 123 ]
}

@test "_getopts --warning" {
	run _getopts --warning
	[ "$status" -eq 3 ]
}
