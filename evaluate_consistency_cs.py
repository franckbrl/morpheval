#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import math

from collections import Counter


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
        tag.append(line[2])
        

def eval_noun(sents, tags, morph):
    # find words to evaluate
    index = {}
    for i, sent in enumerate(sents):
        index[i] = set()
        for j, sent_comp in enumerate(sents):
            if j == i:
                continue
            for idx in [ii for ii, w in enumerate(sent) if w not in sent_comp]:
                if tags[i][idx][0] == 'N':
                    index[i].add(idx)
        index[i] = list(index[i])
                    
    case = Counter()
    wait = []
    for ind_sent, idx in index.items():
        if len(idx) > 1:
            # process other sentences and finally
            # choose the most frequent case.
            c = []
            for i in idx:
                c.append(tags[ind_sent][i][4])
            wait.append(c)
        elif len(idx) == 0:
            case['U'] += 1
        else:
            c = tags[ind_sent][idx[0]][4]
            case[c] += 1


    # if X and another tag for one hypothesis,
    # remove X.
    new_wait = []
    for w in wait:
        while 'X' in w:
            w.remove('X')
        if w == []:
            case['X'] += 1
        else:
            new_wait.append(w)
    wait = list(new_wait)

    if wait:
        # now count ambiguities
        wait_set = [set(x) for x in wait]
        inter = set.intersection(*wait_set)
        # take the intersection of all wait lists
        if inter:
            wait = [list(inter) for x in wait]

        for w in wait:
            max_choice = None
            max_freq = 0
            for c in w:
                if case[c] >= max_freq:
                    max_choice = c
                    max_freq = case[c]
            case[max_choice] += 1

    if 'X' in case:
        max_c = 'X'
        max_f = 0

        for c in case:
            if case[c] > max_f and c not in ['X', 'U']:
                max_c = c
                max_f = case[c]
        n = case['X']
        del case['X']
        case[max_c] += n

    # compute entropy
    # 5 sentences
    max_ent = math.log(5)
    # Spread 'U' count into different predictions
    # (predicting 5 times 'U' should not be a good thing)
    if 'U' in case and case['U'] > 1:
        for i in range(case['U']):
            case['U'+str(i)] = 1
        del case['U']
    ent = sum([((case[c]/5) * math.log(case[c]/5)) for c in case])
    return - ent/max_ent


def eval_adj(sents, tags, morph):
    # find words to evaluate
    index = {}
    for i, sent in enumerate(sents):
        index[i] = set()
        for j, sent_comp in enumerate(sents):
            if j == i:
                continue
            for idx in [ii for ii, w in enumerate(sent) if w not in sent_comp]:
                if tags[i][idx][0] == 'A':
                    index[i].add(idx)
        index[i] = list(index[i])
                    
    gender = Counter()
    number = Counter()
    case = Counter()
    wait_g = []
    wait_n = []
    wait_c = []
    for ind_sent, idx in index.items():
        if len(idx) > 1:
            # process other sentences and finally
            # choose the most frequent case.
            g = []
            n = []
            c = []
            for i in idx:
                g.append(tags[ind_sent][i][2])
                n.append(tags[ind_sent][i][3])
                c.append(tags[ind_sent][i][4])
            wait_g.append(g)
            wait_n.append(n)
            wait_c.append(c)
        elif len(idx) == 0:
            # unk tag
            gender['U'] += 1
            number['U'] += 1
            case['U'] += 1
        else:
            idx = idx[0]
            g = tags[ind_sent][idx][2]
            n = tags[ind_sent][idx][3]
            c = tags[ind_sent][idx][4]
            gender[g] += 1
            number[n] += 1
            case[c] += 1

    # if X and another tag for one hypothesis,
    # remove X.
    new_wait = []
    for w in wait_g:
        while 'X' in w:
            w.remove('X')
        if w == []:
            case['X'] += 1
        else:
            new_wait.append(w)
    wait_g = list(new_wait)

    if wait_g:
        # now count ambiguities
        wait_set = [set(x) for x in wait_g]
        inter = set.intersection(*wait_set)
        # take the intersection of all wait lists
        if inter:
            wait_g = [list(inter) for x in wait_g]
        for w in wait_g:
            max_choice= None
            max_freq = 0
            for g in w:
                if gender[g] >= max_freq:
                    max_choice = g
                    max_freq = gender[g]
            gender[max_choice] += 1

    new_wait = []
    for w in wait_n:
        while 'X' in w:
            w.remove('X')
        if w == []:
            case['X'] += 1
        else:
            new_wait.append(w)
    wait_n = list(new_wait)

    if wait_n:
        # now count ambiguities
        wait_set = [set(x) for x in wait_n]
        inter = set.intersection(*wait_set)
        # take the intersection of all wait lists
        if inter:
            wait_n = [list(inter) for x in wait_n]
        for w in wait_n:
            max_choice= None
            max_freq = 0
            for n in w:
                if number[n] >= max_freq:
                    max_choice = n
                    max_freq = number[n]
            number[max_choice] += 1

    new_wait = []
    for w in wait_c:
        while 'X' in w:
            w.remove('X')
        if w == []:
            case['X'] += 1
        else:
            new_wait.append(w)
    wait_c = list(new_wait)

    if wait_c:
        # now count ambiguities
        wait_set = [set(x) for x in wait_c]
        inter = set.intersection(*wait_set)
        # take the intersection of all wait lists
        if inter:
            wait_c = [list(inter) for x in wait_c]
        for w in wait_c:
            max_choice= None
            max_freq = 0
            for c in w:
                if case[c] >= max_freq:
                    max_choice = c
                    max_freq = case[c]
            case[max_choice] += 1

    # try to get only 3 genders
    masc = gender['I'] + gender['M'] + gender['Y']
    del gender['I']
    del gender['Y']
    gender['M'] = masc
    # H, Q
    g = gender['H'] + gender['Q']
    del gender['H']
    del gender['Q']
    if gender['F'] > gender['N']:
        gender['F'] += g
    else:
        gender['N'] += g
    # T
    if gender['M'] > gender['F']:
        gender['M'] += gender['T']
    else:
        gender['F'] += gender['T']
    del gender['T']
    # Z
    if gender['M'] > gender['N']:
        gender['M'] += gender['Z']
    else:
        gender['F'] += gender['Z']
    del gender['Z']

    # 2 numbers
    number['P'] += number['D']
    del number['D']
    if number['S'] > number['P']:
        number['S'] += number['W']
    else:
        number['P'] += number['W']
    del number['W']

    # remove X tag
    max_gender = 'X'
    max_g_freq = 0
    max_number = 'X'
    max_n_freq = 0
    max_case = 'X'
    max_c_freq = 0 

    for g in gender:
        if gender[g] > max_g_freq and g not in ['X', 'U']:
            max_gender = g
            max_g_freq = gender[g]
    if max_gender != 'X':
        gender[max_gender] += gender['X']
        del gender['X']

    for n in number:
        if number[n] > max_n_freq and n not in ['X', 'U']:
            max_number = n
            max_n_freq = number[n]
    if max_number != 'X':
        number[max_number] += number['X']
        del number['X']

    for c in case:
        if case[c] > max_c_freq and c not in ['X', 'U']:
            max_case = c
            max_c_freq = case[c]
    if max_case != 'X':
        case[max_case] += case['X']
        del case['X']

    # compute entropy
    # 4 genders, 3 numbers, 8 cases ('U' included)
    # 5 sentences
    max_ent_g = max_ent_n = max_ent_c = - math.log(5)
    # Spread 'U' count into different predictions
    # (predicting 5 times 'U' should not be a good thing)
    if 'U' in gender and gender['U'] > 1:
        for i in range(gender['U']):
            gender['U'+str(i)] = 1
        del gender['U']
    if 'U' in number and number['U'] > 1:
        for i in range(number['U']):
            number['U'+str(i)] = 1
        del number['U']
    if 'U' in case and case['U'] > 1:
        for i in range(case['U']):
            case['U'+str(i)] = 1
        del case['U']
    ent_g = sum([((gender[g]/5) * math.log(gender[g]/5)) for g in gender if gender[g] > 0])
    ent_n = sum([((number[n]/5) * math.log(number[n]/5)) for n in number if number[n] > 0])
    ent_c = sum([((case[c]/5) * math.log(case[c]/5)) for c in case if case[c] > 0])
    return ent_g/max_ent_g, ent_n/max_ent_n, ent_c/max_ent_c

def eval_verb(sents, tags, morph):
    # find words to evaluate
    index = {}
    for i, sent in enumerate(sents):
        index[i] = set()
        for j, sent_comp in enumerate(sents):
            if j == i:
                continue
            for idx in [ii for ii, w in enumerate(sent) if w not in sent_comp]:
                if tags[i][idx][0] == 'V':
                    index[i].add(idx)
        index[i] = list(index[i])
                    
    number = Counter()
    person = Counter()
    tense = Counter()
    negation = Counter()
    wait_nb = []
    wait_ps = []
    wait_tm = []
    wait_ne = []
    for ind_sent, idx in index.items():
        if len(idx) > 1:
            # process other sentences and finally
            # choose the most frequent case.
            nb = []
            ps = []
            tm = []
            ne = []
            for i in idx:
                nb.append(tags[ind_sent][i][3])
                ps.append(tags[ind_sent][i][7])
                tm.append(tags[ind_sent][i][8])
                ne.append(tags[ind_sent][i][10])
            wait_nb.append(nb)
            wait_ps.append(ps)
            wait_tm.append(tm)
            wait_ne.append(ne)
        elif len(idx) == 0:
            # unk tag
            number['U'] += 1
            person['U'] += 1
            tense['U'] += 1
            negation['U'] += 1
        else:
            idx = idx[0]
            nb = tags[ind_sent][idx][3]
            ps = tags[ind_sent][idx][7]
            tm = tags[ind_sent][idx][8]
            ne = tags[ind_sent][idx][10]
            number[nb] += 1
            person[ps] += 1
            tense[tm] += 1
            negation[ne] += 1

    # if X and another tag for one hypothesis,
    # remove X.
    new_wait = []
    for w in wait_nb:
        while 'X' in w:
            w.remove('X')
        if w == []:
            number['X'] += 1
        else:
            new_wait.append(w)
    wait_nb = list(new_wait)

    if wait_nb:
        # now count ambiguities
        wait_set = [set(x) for x in wait_nb]
        inter = set.intersection(*wait_set)
        # take the intersection of all wait lists
        if inter:
            wait_nb = [list(inter) for x in wait_nb]
        for w in wait_nb:
            max_choice= None
            max_freq = 0
            for nb in w:
                if number[nb] >= max_freq:
                    max_choice = nb
                    max_freq = number[g]
            number[max_choice] += 1

    new_wait = []
    for w in wait_ps:
        while 'X' in w:
            w.remove('X')
        if w == []:
            person['X'] += 1
        else:
            new_wait.append(w)
    wait_ps = list(new_wait)

    if wait_ps:
        # now count ambiguities
        wait_set = [set(x) for x in wait_ps]
        inter = set.intersection(*wait_set)
        # take the intersection of all wait lists
        if inter:
            wait_ps = [list(inter) for x in wait_ps]
        for w in wait_ps:
            max_choice= None
            max_freq = 0
            for n in w:
                if person[n] >= max_freq:
                    max_choice = n
                    max_freq = person[n]
            person[max_choice] += 1

    new_wait = []
    for w in wait_tm:
        while 'X' in w:
            w.remove('X')
        if w == []:
            tense['X'] += 1
        else:
            new_wait.append(w)
    wait_tm = list(new_wait)

    if wait_tm:
        # now count ambiguities
        wait_set = [set(x) for x in wait_tm]
        inter = set.intersection(*wait_set)
        # take the intersection of all wait lists
        if inter:
            wait_tm = [list(inter) for x in wait_tm]
        for w in wait_tm:
            max_choice= None
            max_freq = 0
            for n in w:
                if tense[n] >= max_freq:
                    max_choice = n
                    max_freq = tense[n]
            tense[max_choice] += 1

    new_wait = []
    for w in wait_ne:
        while 'X' in w:
            w.remove('X')
        if w == []:
            negation['X'] += 1
        else:
            new_wait.append(w)
    wait_ne = list(new_wait)

    if wait_ne:
        # now count ambiguities
        wait_set = [set(x) for x in wait_ne]
        inter = set.intersection(*wait_set)
        # take the intersection of all wait lists
        if inter:
            wait_ne = [list(inter) for x in wait_ne]
        for w in wait_ne:
            max_choice = None
            max_freq = 0
            for c in w:
                if negation[c] >= max_freq:
                    max_choice = c
                    max_freq = negation[c]
            negation[max_choice] += 1

    # ambiguous tense
    if tense['R'] > tense['P']:
        tense['R'] += tense['H']
    else:
        tense['P'] += tense['H']

    # remove X tag
    max_number = 'X'
    max_nb_freq = 0
    max_person = 'X'
    max_ps_freq = 0
    max_tense = 'X'
    max_tm_freq = 0 
    max_negation = 'X'
    max_ne_freq = 0 
    
    for nb in number:
        if number[nb] > max_nb_freq and nb not in ['X', 'U']:
            max_number = nb
            max_nb_freq = number[nb]
    if max_number != 'X':
        number[max_number] += number['X']
        del number['X']

    for ps in person:
        if person[ps] > max_ps_freq and ps not in ['X', 'U']:
            max_person = ps
            max_ps_freq = person[ps]
    if max_person != 'X':
        person[max_person] += person['X']
        del person['X']

    for tm in tense:
        if tense[tm] > max_tm_freq and tm not in ['X', 'U']:
            max_tense = tm
            max_tm_freq = tense[tm]
    if max_tense != 'X':
        tense[max_tense] += tense['X']
        del tense['X']

    for ne in negation:
        if negation[ne] > max_ne_freq and ne not in ['X', 'U']:
            max_negation = ne
            max_ne_freq = negation[ne]
    if max_negation != 'X':
        negation[max_negation] += negation['X']
        del negation['X']

    # compute entropy
    # 5 sentences
    max_ent = - math.log(5)
    # Spread 'U' count into different predictions
    # (predicting 5 times 'U' should not be a good thing)
    if 'U' in number and number['U'] > 1:
        for i in range(number['U']):
            number['U'+str(i)] = 1
        del number['U']
    if 'U' in person and person['U'] > 1:
        for i in range(person['U']):
            person['U'+str(i)] = 1
        del person['U']
    if 'U' in tense and tense['U'] > 1:
        for i in range(tense['U']):
            tense['U'+str(i)] = 1
        del tense['U']
    if 'U' in negation and negation['U'] > 1:
        for i in range(negation['U']):
            negation['U'+str(i)] = 1
        del negation['U']

    ent_nb = sum([((number[nb]/5) * math.log(number[nb]/5)) for nb in number if number[nb] > 0])
    ent_ps = sum([((person[ps]/5) * math.log(person[ps]/5)) for ps in person if person[ps] > 0])
    ent_tm = sum([((tense[tm]/5) * math.log(tense[tm]/5)) for tm in tense if tense[tm] > 0])
    ent_ne = sum([((negation[ne]/5) * math.log(negation[ne]/5)) for ne in negation if negation[ne] > 0])
    return ent_nb/max_ent, ent_ps/max_ent, ent_tm/max_ent, ent_ne/max_ent



parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='i', nargs="?", type=argparse.FileType('r'),
                    help="input morphodita analysis")
parser.add_argument('-n', dest='n', nargs="?", type=argparse.FileType('r'),
                    help="input info file")
parser.add_argument('-l', '--latex', dest='latex', action='store_true',
                    help="output in latex format")
args = parser.parse_args()

ent_n = 0
total_n = 0
ent_adj_gend = 0
ent_adj_numb = 0
ent_adj_case = 0
total_adj = 0
ent_v_nb = 0
ent_v_ps = 0
ent_v_tm = 0
ent_v_ne = 0
total_v = 0

for sents, tags, morph in get_pairs(args.i, args.n):

    if morph == 'syns_adj':
        g, n, c = eval_adj(sents, tags, morph)
        ent_adj_gend += g
        ent_adj_numb += n
        ent_adj_case += c
        total_adj += 1

    elif morph == 'syns_noun':
        ent_n += eval_noun(sents, tags, morph)
        total_n += 1

    elif morph == 'syns_verb':
        nb, ps, tm, ne = eval_verb(sents, tags, morph)
        ent_v_nb += nb
        ent_v_ps += ps
        ent_v_tm += tm
        ent_v_ne += ne
        total_v += 1

if not args.latex:
    print("noun case: {:.3f}".format(ent_n/total_n))
    print("adj gender: {:.3f}".format(ent_adj_gend/total_adj))
    print("adj number: {:.3f}".format(ent_adj_numb/total_adj))
    print("adj case: {:.3f}".format(ent_adj_case/total_adj))
    print("verb number {:.3f}".format(ent_v_nb/total_v))
    print("verb person {:.3f}".format(ent_v_ps/total_v))
    print("verb tense {:.3f}".format(ent_v_tm/total_v))
    print("verb negation {:.3f}".format(ent_v_ne/total_v))

else:
    mean=sum([ent_n/total_n, ent_adj_gend/total_adj, ent_adj_numb/total_adj, ent_adj_case/total_adj, ent_v_nb/total_v, ent_v_ps/total_v, ent_v_tm/total_v, ent_v_ne/total_v]) / 8.
    latex=[ent_n/total_n, ent_adj_gend/total_adj, ent_adj_numb/total_adj, ent_adj_case/total_adj, ent_v_nb/total_v, ent_v_ps/total_v, ent_v_tm/total_v, ent_v_ne/total_v, mean]

    print("{:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} \\\\ ".format(*latex))

