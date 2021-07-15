#!/usr/bin/env python3

import cqviewer

this = cqviewer.wsjtx2df('example/data_short.TXT')

that = cqviewer.df2heatmap(this)
print(that)
