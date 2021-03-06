#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse

from collections import defaultdict
from itertools import permutations


def get_pairs(text, info):
    info = [l.split() for l in info]
    sent_id = info[0][0]  # get 1st sentence ID.
    sents = []
    tags = []
    sent = []
    tag = []
    i = 0
    for line in text:
        if line == '\n':
            sents.append(sent)
            tags.append(tag)
            sent = []
            tag = []
            # new sentence
            i += 1
            continue
        line = line.split()
        # new sentence group
        if sent_id != info[i][0]:
            yield sents, tags, info[i-1][1]
            sents = []
            tags = []
            sent_id = info[i][0]
        # add words and tags
        sent.append(line[0])
        ii = 1
        t = []
        while ii < len(line):
            t.append(line[ii])
            ii += 1
        tag.append(t)
    # last sentence
    yield sents, tags, info[-1][1]


def evaluate(sents, tags, morph, subcat=None):
    # get words from the 2nd sentence that
    # are not in the 1st sentence
    index = [i for i, w in enumerate(sents[1]) if w not in sents[0]]
    # both sentences are identical
    if index == []:
        return 0

    if morph == 'preposition':
        # words in sentence 2 that are not in 1 and vice-versa.
        index1 = [i for i, w in enumerate(sents[1]) if w not in sents[0]]
        index2 = [i for i, w in enumerate(sents[0]) if w not in sents[1]]
        res1 = 0
        for i in index1:
            case_prep = [t[3] for t in tags[1][i] if t[0] == 's']
            if case_prep == []:
                continue
            # look for the noun on the left
            if i < len(sents[1])-1:
                for j, tag in enumerate(tags[1][i+1:], i+1):
                    tag = [t for t in tag if t[0] == 'n']
                    if tag != []:
                        case_noun = [t[4] for t in tag]
                        if list(set(case_prep).intersection(case_noun)) != [] or '_' in case_noun:
                            res1 = 1

        res2 = 0
        for i in index2:
            case_prep = [t[3] for t in tags[0][i] if t[0] == 's']
            if case_prep == []:
                continue
            # look for the noun on the left
            if i < len(sents[0])-1:
                for j, tag in enumerate(tags[0][i+1:], i+1):
                    tag = [t for t in tag if t[0] == 'n']
                    if tag != []:
                        case_noun = [t[4] for t in tag]
                        if list(set(case_prep).intersection(case_noun)) != [] or '_' in case_noun:
                            res2 = 1

        return res1 + res2


    if morph == 'coordverb':
        new_verb = []
        for i in index:
            tag_is = list(set([(i, (t[7], t[8], t[5])) for t in tags[1][i] if t[0] == 'v']))
            new_verb.append(tag_is)
        new_verb = [n for n in new_verb if n != []]
        if new_verb == []:
            return 0
        n = ['person', 'number', 'tense'].index(subcat)
        for word in new_verb:
            for analysis in word:
                i = analysis[0]
                tag = analysis[1][n]
                # go to the right and find the second verb
                # todo: check if sents[1][j] is in sents[0]
                # and count (system consistency).
                for j, tag2 in enumerate(tags[1][i+1:], i+1):
                    tag_right = list(set([(t[7], t[8], t[5]) for t in tag2 if t[0] == 'v']))
                    if tag_right == []:
                        continue
                    for tag_r_full in tag_right:
                        tag_r = tag_r_full[n]
                        # Present perfective forms
                        if tag_r == tag or tag_r == '_' or tag == '_':
                            # if subcat == 'tense' and tag_r == 'P' and (tag_r_full[-1] == 'B' or analysis[1][-1] == 'B'):
                            #     if tag_r_full[-1] == analysis[1][-1] == 'B':
                            #         return 1
                            #     else:
                            #         return 0
                            # if subcat == 'tense' and (tag_r_full[-1] == 'f' or analysis[1][-1] == 'f'):
                            #     if tag_r_full[-1] == analysis[1][-1]:
                            #         return 1
                            #     else:
                            #         return 0
                            return 1
        return 0

    if morph == 'pron2coord':
        noun = []
        for i in index:
            tag_is = list(set([t[4] for t in tags[1][i] if t[0] == 'n']))
            noun.append(tag_is)
        noun = [n for n in noun if n != []]
        if len(noun) < 2:
            return 0
        done = []
        for n1, n2 in permutations(noun, 2):
            if (n2, n1) in done:
                continue
            done.append((n1, n2))
            inter = list(set(n1).intersection(n2))
            if inter != []:
                continue
            else:
                return 1
        return 0

    if morph == 'pron2nouns':
        adj = [t[2:5] for i, w in enumerate(tags[1]) for t in w if t[0] == 'a' and i in index]
        noun = [t[2:5] for i, w in enumerate(tags[1]) for t in w if t[0] == 'n' and i in index]
        if adj == [] or noun == []:
            return 0
        n = ['gender', 'number', 'case'].index(subcat)
        feat_adj = [t[n] for t in adj]
        feat_noun = [t[n] for t in noun]
        # merge dual and plural
        feat_adj = ['p' if x == 'd' else x for x in feat_adj]
        feat_noun = ['p' if x == 'd' else x for x in feat_noun]
        inter = list(set(feat_adj).intersection(feat_noun))
        if inter != []:
            return 1
        else:
            return 0

    for i in index:

        if morph == 'future':
            feature = [t[5] for t in tags[1][i] if t[0] == 'v']
            if 'f' in feature or '_' in feature:
                return 1

        elif morph == 'past':
            feature = [t[5] for t in tags[1][i] if t[0] == 'v']
            if 's' in feature or '_' in feature:
                return 1

        # elif morph == 'comparative':
        #     feature = [t[6] for t in tags[1][i] if t[0] == 'a']
        #     if 'c' in feature:
        #         return 1
        #     if sents[1][i] == 'daudz':
        #         return 1
    
        # elif morph == 'negation':
        #     feature = [t[-1] for t in tags[1][i] if t[0] == 'v']
        #     if 'y' in feature:
        #         return 1   

        elif morph == 'noun_number':
            feature = [t[3] for t in tags[1][i] if t[0] == 'n']
            if 'p' in feature or 'd' in feature or '_' in feature:
                return 1  

        elif morph == 'pron_fem':
            feature = [t[3] for t in tags[1][i] if t[0] == 'p']
            if 'f' in feature or '0' in feature or '_' in feature:
                return 1    

        elif morph == 'pron_plur':
            feature = [t[4] for t in tags[1][i] if t[0] == 'p']
            if 'p' in feature or '0' in feature or '_' in feature:
                return 1   

    return 0



parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='i', nargs="?", type=argparse.FileType('r'),
                    help="input morphodita analysis")
parser.add_argument('-n', dest='n', nargs="?", type=argparse.FileType('r'),
                    help="input info file")
parser.add_argument('-l', '--latex', dest='latex', action='store_true',
                    help="output in latex format")
args = parser.parse_args()

correct = 0
total = 0

results = defaultdict(lambda: 0)
total = defaultdict(lambda: 0)

for sents, tags, morph in get_pairs(args.i, args.n):
    if len(sents) == len(tags) == 2 and not morph.startswith('syns'):
        subcat = None
        if ':' in morph:
            morph, subcat = morph.split(':')
            if subcat == 'time':
                subcat = 'tense'

        if morph in ['pron2nouns']:
            pass
            for subcat in ['gender', 'number', 'case']:
                inf = morph+':'+subcat
                results[inf] += evaluate(sents, tags, morph, subcat)
                total[inf] += 1

        elif morph in ['coordverb']:
            pass
            for subcat in ['person', 'number', 'tense']:
                inf = morph+':'+subcat
                results[inf] += evaluate(sents, tags, morph, subcat)
                total[inf] += 1

        elif morph in ['preposition']:
            pass
            results[morph] += evaluate(sents, tags, morph, subcat)
            total[morph] += 2
                
        else:
            results[morph] += evaluate(sents, tags, morph, subcat)
            total[morph] += 1

if not args.latex:
    for res, nb in sorted(results.items()):
        if res in ['negation', 'comparative']:
            continue
        print("{}:\t{:.1f}% ({}/{})".format(res, nb/total[res]*100, nb, total[res]))

else:
    a_feat = ['past',
    'future',
    'pron_fem',
    'pron_plur',
    'noun_number'
    ]
    meanA = sum([results[m]/total[m]*100 for m in a_feat])/len(a_feat)
    latexA = [results[m]/total[m]*100 for m in a_feat] + [meanA]
    print("A-set: {:.1f}\% & {:.1f}\% & {:.1f}\% & {:.1f}\% & {:.1f}\% & {:.1f}\% \\\\ ".format(*latexA))

    b_feat = ['coordverb:number',
    'coordverb:person',
    'coordverb:tense',
    'pron2coord',
    'pron2nouns:gender',
    'pron2nouns:number',
    'pron2nouns:case',
    'preposition']
    meanB = sum([results[m]/total[m]*100 for m in b_feat])/len(b_feat)
    latexB = [results[m]/total[m]*100 for m in b_feat] + [meanB]
    print("B-set: {:.1f}\% & {:.1f}\% & {:.1f}\% & {:.1f}\% & {:.1f}\% & {:.1f}\% & {:.1f}\% & {:.1f}\% & {:.1f}\% \\\\ ".format(*latexB))

