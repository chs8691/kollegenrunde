#!/bin/bash

ROOT_DST="../content/posts"
IMG="images"
TEMPLATE="../archetypes/post.md"

# case in-sensitive  matching
shopt -s nocaseglob

if [ "$1" == '-h' ]
  then 
    echo "Converter for a post's images and/or creates index.md Usage:"
    echo "convert PATH/ [images,post]"
    echo "  Basename of PATH must be a directory in $ROOT_DST/<DIR>/$IMG (or will be created   )"
    echo "  For instance: convert /media/diskstation/photo/chris/kollegenrunde/20031102\ Conconitest/ images past"
    echo "With the optional parameter 'images', the image converting will be processed"
    echo "With the optional parameter 'post', the index.md file will be created"
    echo "The script must be executed in sub directory 'redaktion'"
  exit 0
fi

if [ -z "$1" ]
  then echo "Missing path, e. g. 'Call convert in/posts/20030412"
  exit 1
fi

PARAM_IMAGES=""
PARAM_POST=""

if [ -z "$2" ]
  then echo "Missing second parameter."
  exit 1
fi

if [ "$2" == "images" ]
    then PARAM_IMAGES="true"
elif [ "$2" == "post" ]
    then PARAM_POST="true"
else 
    echo "Second parameter must be images pr post"
fi

if [ ! -z "$3" ] 
    then 
        if [ "$3" == "images" ]
        then PARAM_IMAGES="true"
    elif [ "$3" == "post" ]
       then PARAM_POST="true"
    else 
        echo "Third parameter must be images or post"
    fi
fi

SRC="$1"
DIR=$(basename $1)
DST="$ROOT_DST/$DIR/$IMG"

if [ $PARAM_IMAGES ]
    then

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
fi
    
##############################
# Create index.md
##############################
if [ $PARAM_POST ]
    then
    echo Create post file
    if [ ! -e $TEMPLATE ]
        then echo "Template '$TEMPLATE' not found !"
        exit 1
    fi
    
    DST2="$ROOT_DST/$DIR/index.md"
    echo DST2=$DST2
    
    NAME=$(basename $TEMPLATE)
    DST3="$ROOT_DST/$DIR/$NAME"
    echo DST3=$DST3

    cp $TEMPLATE "$DST3"

    # Set title     
    sed -i -e "s/title: .*/title: \"$DIR\"/g" $DST3

    # Set Date
    sed -i -e "s/date: .*/date: ${DIR:0:4}-${DIR:4:2}-${DIR:6:2}/g" $DST3

    # Take first image as featured / header image
    echo dst=$DST
    FILES=($DST/*)
    FIRST=${FILES[0]}
    
    if [ -e $FIRST ]
        then
        FILE=$(basename $FIRST)
        echo "file=$FILE"
        sed -i -e "s/header_image:.*/header_image: images\/$FILE/g" $DST3
        sed -i -e "s/featured_image:.*/featured_image: images\/$FILE/g" $DST3
            
    fi
 
    echo "$DST3" created
    
    if [ -e $DST2 ]
        then echo "File '$DST2' already exists and will not be overwritten !"
        exit 1
    fi
    
    mv $DST3 $DST2
    
    
fi
    


shopt -u nullglob # Unsets nullglob
shopt -u nocaseglob
