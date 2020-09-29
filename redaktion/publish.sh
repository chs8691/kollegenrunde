#!/bin/bash

echo Publish to Uberspace...

rsync -avv --delete /home/chris/hugo/kollegenrunde/public/ kollegen@despina.uberspace.de:html/kollegenrunde
