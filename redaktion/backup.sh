#!/bin/bash

rsync -avz --delete --exclude kollegenrunde/.git --exclude kollegenrunde/public/ --exclude *swp /home/chris/hugo /media/diskstation/externalAccess/rsyncs
