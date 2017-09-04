#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

i = 1
for line in sys.stdin:
    line = line.rstrip()
    if line == '':
        print()
        i = 0
        continue
    line = [str(i)] + [line] + (['_'] * 8)
    print('\t'.join(line))
    i += 1
