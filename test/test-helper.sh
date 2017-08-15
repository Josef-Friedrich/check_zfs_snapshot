#! /bin/sh

# MIT License
#
# Copyright (c) 2017 Josef Friedrich <josef@friedrich.rocks>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

mock_path() {
	_rm_dash() {
		echo $@ | sed 's#/*$##'
	}
	SAVEIFS=$IFS
	IFS=:
	local TMP_PATH
	TMP_PATH=
	if [ -n "$PARENT_MOCK_PATH" ]; then
		for P in $1 ; do
			TMP_PATH="${TMP_PATH}$(_rm_dash $PARENT_MOCK_PATH)/$(_rm_dash $P):"
		done
		export PATH="${TMP_PATH}${PATH}"
	else
		export PATH="$(_rm_dash $1):${PATH}"
	fi
	IFS=$SAVEIFS
}

source_exec() {
	local TMP_FILE
	TMP_FILE=$(mktemp)
	local SEPARATOR
	SEPARATOR='## This SEPARATOR is required for test purposes. Please don’t remove! ##'
	if [ -n "$SOURCE_EXEC_SEPARATOR" ]; then
		SEPARATOR="$SOURCE_EXEC_SEPARATOR"
	fi
	if [ -f "$1" ]; then
		sed "/$SEPARATOR/Q" "$1" > "$TMP_FILE"
		. "$TMP_FILE"
	else
		echo "The file “$1” doesn’t exist and therefore couldn’t be sourced!"
	fi
}
