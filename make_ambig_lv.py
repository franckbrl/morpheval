#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import pickle

parser = argparse.ArgumentParser()

parser.add_argument('-w', dest='words', nargs='?', type=argparse.FileType('r'))
parser.add_argument('-t', dest='tags', nargs='?', type=argparse.FileType('r'))
parser.add_argument('-d', dest='dic', nargs='?', type=str,
                    default='utils/latvian_dict.pkl')
args = parser.parse_args()

dic = pickle.load(open(args.dic, 'rb'), encoding='utf-8')

for words, tags in zip(args.words, args.tags):
    for word, tag in zip(words.split(), tags.rstrip().split('\t')):
        tag = tag.split()
        lem = tag[0]
        tag_bag = set()
        tag_bag.add(''.join(tag[1:]))
        if lem in dic:
            for form, t in dic[lem]:
                if form == word:
                    # if the tag was predicted less
                    # than 100 times for the word,
                    # remove it (avoid obvious noise).
                    if dic[lem][(form, t)] > 100:
                        tag_bag.add(t)
        print(word + '\t' + '\t'.join([w for w in tag_bag]))
    print()
