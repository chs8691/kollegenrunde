#!/bin/bash

ROOT_SRC="/home/chris/hugo/kollegenrunde/redaktion/in/posts"
ROOT_DST="/home/chris/hugo/kollegenrunde/content/posts"
IMG="images"

# case in-sensitive  matching
shopt -s nocaseglob

if [ "$1" == '-h' ]
  then 
    echo "Converter for a post's images. Usage:"
    echo "convert DATE"
    echo "  DATE must be a directory in $ROOT_DST/<DATA>/$IMG"
    echo "  Images will be used in $ROOT_SRC/<DATA>/$IMG"
    echo "  For instance: convert 20200912"
  exit 0
fi

if [ -z "$1" ]
  then echo "Missing post date, e. g. 'Call convert 20200912'"
  exit 1
fi

SRC="$ROOT_SRC/$1/$IMG"
DST="$ROOT_DST/$1/$IMG"

if [ ! -e $SRC ]
  then echo "Directory '$SRC' not found !"
  exit 1
fi

if [ ! -e $ROOT_DST ]
  then echo "Destination root directory '$ROOT_DST' not found !"
  exit 1
fi

if [ ! -e "$ROOT_DST/$1" ]
  then echo "Create $ROOT_DST/$1"
  mkdir "$ROOT_DST/$1"
fi

echo "Create images for $1..."


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
