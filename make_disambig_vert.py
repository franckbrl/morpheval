#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-w', dest='words', nargs='?', type=argparse.FileType('r'))
parser.add_argument('-t', dest='tags', nargs='?', type=argparse.FileType('r'))
args = parser.parse_args()

for words, tags in zip(args.words, args.tags):
    for word, tag in zip(words.split(), tags.rstrip().split('\t')):
        tag = tag.split()
        lem = tag[0]
        tag = ''.join(tag[1:])
        print(word + '\t' + tag)
    print()
