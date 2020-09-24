#!/bin/bash

ROOT_DST="/home/chris/hugo/kollegenrunde/content/posts"
IMG="images"

# case in-sensitive  matching
shopt -s nocaseglob

if [ "$1" == '-h' ]
  then 
    echo "Converter for a post's images. Usage:"
    echo "convert PATH/"
    echo "  Basename of PATH must be a directory in $ROOT_DST/<DIR>/$IMG (or will be created   )"
    echo "  For instance: convert in/post/20200912"
  exit 0
fi

if [ -z "$1" ]
  then echo "Missing post date, e. g. 'Call convert 20200912'"
  exit 1
fi

SRC="$1"
DIR=$(basename "$1")
DST="$ROOT_DST/$DIR/$IMG"

if [ ! -e $SRC ]
  then echo "Directory '$SRC' not found !"
  exit 1
fi

if [ ! -e $ROOT_DST ]
  then echo "Destination root directory '$ROOT_DST' not found !"
  exit 1
fi

if [ ! -e "$ROOT_DST/$DIR" ]
  then echo "Create $ROOT_DST/$DIR"
  mkdir "$ROOT_DST/$DIR"
fi

echo "Create images for $DIR..."


if [ -e "$DST" ] 
    then 
    echo "Delete $DST"
    rm -r "$DST"
fi

echo "Create $DST"
mkdir "$DST"

# Only the largest size. Downsize should be done in HUGO
echo Converting...
shopt -s nullglob # Sets nullglob to avoid not founds
for f in $SRC/*.{jpg,jpeg};
  do
    BNAME=$(basename $f)
    echo $BNAME
    convert $f -resize 1200x1200 -quality 80 $DST/$BNAME
done
shopt -u nullglob # Unsets nullglob
