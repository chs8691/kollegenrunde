#!/bin/bash

ROOT_DST="/home/chris/hugo/kollegenrunde/redaktion/in/posts"

# case in-sensitive  matching
shopt -s nocaseglob
shopt -s nullglob

if [ "$1" == '-h' ]
  then 
    echo "Copy all images " 
    echo "  from DIR"  
    echo "  to   $ROOT_DST/<DATE>"   
    echo "DIR must be a path to a DATE base directory like 2006010213_STAUFEN"
    echo "Destination directory will be deleted an recreated"
    echo "Usage:"
    echo "  load DIR"
    echo ""
    echo "  DATE must be an existing directory"
    echo "  Images will be copied into $ROOT_DST/<DATE>"
    echo "  For instance: load /mnt/pict/20200912_STAUFEN"
  exit 0
fi

if [ -z "$1" ]
  then echo "Missing source directory, e. g. call 'load /mnt/pict/20200912_STAUFEN'"
  exit 1
fi

DIR=$(basename "$1")
#echo dir=$DIR

DATE=${DIR:0:8}
#echo date=$DATE

if [ ! -e "$1" ]
  then echo "Directory '$1' not found !"
  exit 1
fi

if [ ! -e $ROOT_DST ]
  then echo "Destination root directory '$ROOT_DST' not found !"
  exit 1
fi

DST="$ROOT_DST/$DATE"

if [ ! -e $DST ]
  then echo "Create $DST"
  mkdir "$DST"
fi

echo "Processing $DATE..."

if [ -e "$DST" ] 
    then 
    echo "Delete $DST"
    rm -r "$DST"
fi

echo "Create $DST"
mkdir "$DST"

PATTERN="${1// /\\ }*.jpg"
echo pattern=$PATTERN
if [ ${#PATTERN[@]}  ] 
    then 
    echo copying "$PATTERN"...
    cp -v "$1"/*.jpg "$DST"/
fi


