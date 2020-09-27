#!/bin/bash

echo Publish to Uberspace...

rsync -av --delete /home/chris/hugo/kollegenrunde/public/ kollegen@despina.uberspace.de:html/kollegenrunde
