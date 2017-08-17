#! /bin/sh

export PROJECT_NAME="$(basename "$(pwd)")"

export USAGE="$(./$PROJECT_NAME -h)"

chmod a+x README.md.template.sh

./README.md.template.sh > README.md
