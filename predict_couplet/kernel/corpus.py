#! /usr/bin/env python
#-*- coding:utf-8 -*-

import codecs
import sys
import os
import json

from .utils import DATA_PROCESSED_DIR, DATA_RAW_DIR, split_sentences
from .rhyme import RhymeUtil
from functools import reduce


_corpus_list = [ 'merge_data.txt']


def _parse_corpus(raw_file, json_file):
    print("Parsing %s ..." %raw_file) 
    sys.stdout.flush()
    rdict = RhymeUtil()
    data = []
    with codecs.open(raw_file, 'r', 'utf-8') as fin:
        tags = fin.readline().strip().split('\t')
        line = fin.readline().strip()
        while line:
            toks = line.split('\t')
            poem = {'source':os.path.basename(raw_file)}
            for idx, tok in enumerate(toks):
                if tags[idx] != 'body':
                    poem[tags[idx]] = tok
                else:
                    body = tok
            flag = True
            left = body.find('（')
            while left >= 0:
                right = body.find('）')
                if right < left:
                    flag = False
                    break
                else:
                    body = body[:left]+body[right+1:]
                    left = body.find('（')
            if flag and body.find('）') < 0:
                poem['sentences'] = split_sentences(body)
                for sentence in poem['sentences']:
                    if not reduce(lambda x,ch: x and rdict.has_char(ch), sentence, True):
                        flag = False
                        break
                if flag:
                    data.append(poem)
            line = fin.readline().strip()
    with codecs.open(json_file, 'w', 'utf-8') as fout:
        json.dump(data, fout)
    print("Done (%d poems)" %len(data))
    return data


def _parse_couplet(raw_file, json_file):
    print("Parsing %s ..." %raw_file, end=' ')
    sys.stdout.flush()
    data = []
    with codecs.open(raw_file, 'r', 'utf-8') as fin:
        line1 = fin.readline().strip()
        line2 = fin.readline().strip()
        while line1 and line2:
            poem = {'source':os.path.basename(raw_file)}
            sentence = [line1]
            sentence.append(line2)
            poem['sentences'] = sentence
            data.append(poem)
            line = fin.readline().strip()
            line1 = fin.readline().strip()
            line2 = fin.readline().strip()
    with codecs.open(json_file, 'w', 'utf-8') as fout:
        json.dump(data, fout)
    print("Done (%d poems)" %len(data))
    return data
    

def get_all_corpus():
    corpus = []
    for raw in _corpus_list:
        json_file = os.path.join(DATA_PROCESSED_DIR, raw.replace('all', 'json').replace('txt', 'json'))
        try:
            with codecs.open(json_file, 'r', 'utf-8') as fin:
                data = json.load(fin)
        except IOError:
            if raw != 'merge_data.txt':
                data = _parse_corpus(os.path.join(DATA_RAW_DIR, raw), json_file)
            else:
                data = _parse_couplet(os.path.join(DATA_RAW_DIR, raw), json_file)
        finally:
            corpus.extend(data)
    return corpus


if __name__ == '__main__':
    corpus = get_all_corpus()
    print("Size of the entire corpus: %d" % len(corpus))

