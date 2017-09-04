#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

sent_out = []
for line in sys.stdin:
    line = line.split()
    if line == []:
        print('\t'.join(sent_out))
        sent_out = []
        continue
    lem = line[2]
    tags = ' '.join([t for t in line[3]])
    if len(tags) == 1:
        tags += ' -'
    word = lem + ' ' + tags
    sent_out.append(word)
