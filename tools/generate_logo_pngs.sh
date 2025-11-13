#!/usr/bin/bash

set -e

this_dir=`dirname $(realpath "$0")`
logos_dir="$this_dir/../logo/generated"

for logo in $logos_dir/*svg;
do
    # TODO: this currently results in pngs that are 824x824 for the non-padded logo, which maybe is not
    # what we want. 
    png="${logo%.svg}.png"
    inkscape $logo -o $png
    echo `basename $png`
done
