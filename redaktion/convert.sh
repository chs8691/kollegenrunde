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

FORCE="false"
if [ "$2" = "-f" ] || [ "$3" = "-f" ] || [ "$4" = "-f" ] 
then
  FORCE="true"
fi
echo "force=$FORCE"

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

if [ "$2" = "images" ] || [ "$3" = "images" ] || [ "$4" = "images" ]
    then PARAM_IMAGES="true"
fi

if [ "$2" = "post" ] || [ "$3" = "post" ] || [ "$4" = "post" ]
    then PARAM_POST="true"
else 
    echo "Parameter missing: 'images' and/or 'post'"
    exit 1
fi

#echo "Param images=$PARAM_IMAGES"
#echo "Param post=$PARAM_POST"

SRC="$1"
DIR=$(basename $1)
DST="$ROOT_DST/$DIR/$IMG"
DST2="$ROOT_DST/$DIR/index.md"

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



    if [ -e "$DST" ] 
        then 
        if [ $FORCE = "false" ]
            then echo "$DST already exists! Use 'f' to overwrite images (and index.md)."
            exit 1
        fi
        echo "Create images for $DIR..."

        echo "Delete $DST"
        rm -r "$DST"
    fi

    echo "Create $DST"
    mkdir "$DST"

    # Only the largest size. Downsize should be done in HUGO
    echo Converting...
    shopt -s nullglob # Sets nullglob to avoid not founds
    for f in $SRC/*.{jpg,jpeg,png};
    do
        BNAME=$(basename $f)
        echo $BNAME
        convert $f -resize 1200x1200 -quality 80 $DST/$BNAME
    done
fi
    
###################################################
# Create post.md and rename it to index.md (if new)
###################################################
if [ $PARAM_POST ]
    then
    #echo Create post file
    if [ ! -e $TEMPLATE ]
        then echo "Template '$TEMPLATE' not found !"
        exit 1
    fi
    

    #echo DST2=$DST2
    
    NAME=$(basename $TEMPLATE)
    DST3="$ROOT_DST/$DIR/~$NAME"
    #echo DST3=$DST3

    cp $TEMPLATE "$DST3"

    # Set title     
    sed -i -e "s/title: .*/title: \"$DIR\"/g" $DST3

    # Set Date
    sed -i -e "s/date: .*/date: ${DIR:0:4}-${DIR:4:2}-${DIR:6:2}/g" $DST3

    # Take first image as featured / header image
    #echo dst=$DST
    FILES=($DST/*)
    FIRST=${FILES[0]}
    
    if [ -e $FIRST ]
        then
        FILE=$(basename $FIRST)
        #echo "file=$FILE"
        sed -i -e "s/header_image:.*/header_image: images\/$FILE/g" $DST3
        sed -i -e "s/featured_image:.*/featured_image: images\/$FILE/g" $DST3
            
    fi

    # Create example for caption entries
    LINES=''
    shopt -s nullglob # Sets nullglob to avoid not founds
    for f in $SRC/*.{jpg,jpeg};
    do
        BNAME=$(basename $f)
        LINE="#   - name: images\/$BNAME\n"
        LINES="${LINES}$LINE"
        LINE="#     text: \"\"\n"
        LINES="${LINES}$LINE"
    done
    
    #echo Create captions
    sed -i -e "s/# captions:/# captions: \n$LINES/g" $DST3
    
 
    #echo "$DST3" created. This is just a filled template, but not used in the blog.
    
    if [ -e $DST2 ] && [ $FORCE = "false" ]
        then echo "File '$DST2' already exists! Use -f to overwrite it!"
        exit 1
    else
        mv $DST3 $DST2
        if [ -e $DST2 ] && [ $FORCE = "false" ]
            then echo "$DST2" created. Add your content here.
        else
            echo "$DST2" overwritten. Add your content here.
        fi        
    fi
    
    
    
fi
    


shopt -u nullglob # Unsets nullglob
shopt -u nocaseglob
