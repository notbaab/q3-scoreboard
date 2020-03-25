#!/bin/sh

cp /data/linux/* /home/ioq3srv/ioquake3/patch-files/ && \
cd /home/ioq3srv/q3-logparser && \
pip3 install --user -e . && \
cd /home/ioq3srv/q3-scoreboard && \
pip3 install --user -e . && \
python3 run.py

