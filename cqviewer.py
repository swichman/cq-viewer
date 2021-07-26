#!/usr/bin/env python3

import cqviewer
from time import sleep
from os.path import expanduser

home = expanduser("~")

# this = cqviewer.wsjtx2df('example_data/ALL.TXT')
#
# that = cqviewer.df2heatmap(this, output="test1234", hm_path="cq-heatmap")

this = cqviewer.cqDB(log_name=home + '/.local/share/WSJT-X/ALL.TXT')


while(1):
    this.parse_log()
    sleep(15)
