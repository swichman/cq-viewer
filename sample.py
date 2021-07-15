#!/usr/bin/env python3

import cqviewer

this = cqviewer.wsjtx2df('example/ALL.TXT')

that = cqviewer.df2heatmap(this, "test1234")
