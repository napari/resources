#!/usr/bin/bash

set -e

this_dir=`dirname $(realpath "$0")`
logos_dir="$this_dir/../logo/generated"

for logo in $logos_dir/*svg;
do
    png="${logo%.svg}.png"
    inkscape $logo -o $png -w 1024 -h 1024
    echo `basename $png`
done
