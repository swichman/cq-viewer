#!/usr/bin/env python3

import cqviewer

# this = cqviewer.wsjtx2df('example_data/ALL.TXT')
#
# that = cqviewer.df2heatmap(this, output="test1234", hm_path="cq-heatmap")

this = cqviewer.cqDB(log_name='./example_data/ALL.TXT')

this.parse_log()
