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

FIRST_RELEASE=2017-08-13
VERSION=1.0
PROJECT_PAGES="https://github.com/JosefFriedrich-shell/skeleton"
SHORT_DESCRIPTION='This is the management script of the skeleton.sh project!'
USAGE="$(basename "$0") v$VERSION

Usage: $(basename "$0") [-dhrSsv]

$SHORT_DESCRIPTION

Options:
	-d, --sync-dependencies
	  Sync external dependenices (e. g. test-helper.sh bats)
	-h, --help
	  Show this help message
	-r, --render-readme
	  Render “README.md”.
	-S, -sync-skeleton
	  Sync your project with the skeleton project and update some
	  boilerplate files (e. g. Makefile test/lib/skeleton.sh)
	-s, --short-description
	  Show a short description / summary
	-v, --version
	  Show the version number of this script.
"
PROJECT_NAME="$(basename "$(pwd)")"


# See https://stackoverflow.com/a/28466267

# Exit codes
# Invalid option: 2
# Missing argument: 3
# No argument allowed: 4
_getopts() {
	while getopts ':ab:cdhrSsv-:' OPT ; do
		case $OPT in
			a)
				OPT_ALPHA=1
				;;

			b)
				OPT_BRAVO="$OPTARG"
				;;

			c)
				OPT_CHARLIE=1
				;;

			d) OPT_DEPENDENCIES=1;;
			h) echo "$USAGE"; exit 0;;
			r) OPT_README=1;;
			S) OPT_SKELETON=1;;
			s) echo "$SHORT_DESCRIPTION"; exit 0;;
			v) echo "$VERSION"; exit 0;;

			\?)
				echo "Invalid option “-$OPTARG”!" >&2
				exit 2
				;;

			:)
				echo "Option “-$OPTARG” requires an argument!" >&2
				exit 3
				;;

			-)
				LONG_OPTARG="${OPTARG#*=}"

				case $OPTARG in
					alpha)
						OPT_ALPHA=1
						;;

					bravo=?*)
						OPT_BRAVO="$LONG_OPTARG"
						;;

					charlie)
						OPT_CHARLIE=1
						;;

					sync-dependencies) OPT_DEPENDENCIES=1;;

					alpha*|charlie*)
						echo "No argument allowed for the option “--$OPTARG”!" >&2
						exit 4
						;;

					bravo*)
						echo "Option “--$OPTARG” requires an argument!" >&2
						exit 3
						;;

					help) echo "$USAGE"; exit 0;;
					render-readme) OPT_README=1;;
					sync-skeleton) OPT_SKELETON=1;;
					short-description) echo "$SHORT_DESCRIPTION"; exit 0;;
					version) echo "$VERSION"; exit 0;;

					sync-dependencies*|help*|render-readme*|sync-skeleton*|short-description*|version*)
						echo "No argument allowed for the option “--$OPTARG”!" >&2
						exit 4
						;;

					'')	# "--" terminates argument processing
						break
						;;

					*)
						echo "Invalid option “--$OPTARG”!" >&2
						exit 2
						;;

				esac
				;;

		esac
	done
	GETOPTS_SHIFT=$((OPTIND - 1))
}

_sync_skeleton() {
	_get() {
		mkdir -p "$(dirname "$1")"
		wget -O "$1" "https://raw.githubusercontent.com/JosefFriedrich-shell/skeleton/master/$1"
	}

	_getx() {
		_get "$1"
		chmod a+x "$1"
	}

	_getif() {
		if [ ! -f "$1" ]; then
			_get "$1"
		fi
	}

	_rm() {
		rm -rf "$1"
	}


	_get .travis.yml
	_get Makefile
	_get test/lib/test-helper.sh
	_getif LICENSE
	_getx test/lib/bash_unit
	_getx test/lib/bats/bats
	_getx test/lib/bats/bats-exec-suite
	_getx test/lib/bats/bats-exec-test
	_getx test/lib/bats/bats-format-tap-stream
	_getx test/lib/bats/bats-preprocess
	_getx test/lib/skeleton.sh
	_getx test/lib/test-runner.sh

	_rm README.md.template.sh
	_rm sync-skeleton.sh
	_rm test.sh
	_rm test/bash_unit
	_rm test/lib/render-readme.sh
	_rm test/test-helper.sh
}

_sync_dependencies() {
	_get() {
		mkdir -p "$(dirname "$1")"
		wget -O "$1" "https://raw.githubusercontent.com/$2"
	}

	_get test/lib/bash_unit pgrange/bash_unit/master/bash_unit
	_get test/lib/test-helper.sh JosefFriedrich-shell/test-helper.sh/master/test-helper.sh
	cp skeleton.sh test/lib/skeleton.sh

	rm -rf tmp_bats
	rm -rf test/lib/bats
	git clone https://github.com/sstephenson/bats.git tmp_bats
	mv tmp_bats/libexec test/lib/bats
	rm -rf tmp_bats
}

_render_readme() {

	. ./test/lib/test-helper.sh

	source_exec ./$PROJECT_NAME

	> README.md

	########################################################################

	cat <<EOF >> README.md
[![Build Status](https://travis-ci.org/JosefFriedrich-shell/$PROJECT_NAME.svg?branch=master)](https://travis-ci.org/JosefFriedrich-shell/$PROJECT_NAME)

# $PROJECT_NAME
EOF

	###### README HEADER ###########################################

	echo >> README.md
	[ -f README-header.md ] && cat README-header.md >> README.md
	echo >> README.md

	### SHORT_DESCRIPTION ##########################################

	echo '## Summary / Short description' >> README.md
	echo >> README.md
	echo "> $SHORT_DESCRIPTION" >> README.md
	echo >> README.md

	### USAGE ######################################################

	cat <<'EOF' >> README.md
## Usage

```
EOF
	echo "$USAGE" >> README.md
	echo '```'  >> README.md

	### TESTING ####################################################

	cat <<'EOF' >> README.md
## Testing

```
make test
```
EOF

	### README FOOTER ##############################################

	echo >> README.md
	[ -f README-footer.md ] && cat README-footer.md >> README.md
	cat README.md
}

## This SEPARATOR is required for test purposes. Please don’t remove! ##

_getopts $@
shift $GETOPTS_SHIFT

[ -n "$1" ] && echo "Parameter 1: $1"
[ -n "$2" ] && echo "Parameter 2: $2"

cat <<EOF
      .-.
     (o.o)
      |=|        Welcome to
     __|__       skeleton.sh
   //.=|=.\\
  // .=|=. \\
  \\ .=|=. //
   \\(_=_)//
    (:| |:)
     || ||
     () ()
     || ||
     || ||
    ==' '==
EOF

[ "$OPT_DEPENDENCIES" = 1 ] && _sync_dependencies
[ "$OPT_README" = 1 ] && _render_readme
[ "$OPT_SKELETON" = 1 ] && _sync_skeleton

exit 0
