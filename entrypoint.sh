#!/bin/sh
ls /home/ioq3srv/
cp /data/linux/* /home/ioq3srv/ioquake3/patch-files/
/home/ioq3srv/ioquake3/ioq3ded.x86_64 +exec server.cfg
