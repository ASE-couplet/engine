import json
import codecs
import collections
import jieba.posseg

noun = ['i', 'j', 'l', 'Ng', 'n', 'nr', 'ns', 'nt', 'nz', 's', 't', 'vn', 'tg']
adj = ['Ag', 'a', 'ad', 'an', 'd']

rank_path = "./word_ranks.json"
f = open('rank_words.txt','w',encoding='utf-8')
with codecs.open(rank_path, 'r', 'utf-8') as fin:
    ranks = json.load(fin)
    for rank in ranks:
        f.write(str(rank)+'\n')
    print(ranks)
with open('kw_train.txt','r',encoding='utf-8') as fin:
    c = collections.Counter()
    for line in fin.readlines():
        kw = line.strip().split()
        c.update(kw)
    print(c)
    print(len(c))
f = open('rank_key_words.txt','w',encoding='utf-8')
kw_pos = []
noun_kw = []
adj_kw = []
other_kw = []
noun_file = open('noun_key_words.txt','w',encoding='utf-8')
adj_file = open('adj_key_words.txt','w',encoding='utf-8')
other_file = open('other_key_words.txt','w',encoding='utf-8')
for kw in c.most_common():
    poss = jieba.posseg.cut(kw[0])
    for x in poss:
        word, pos = x.word, x.flag
        kw_pos.append([word, pos, kw[1]])
        if pos in noun:
            noun_kw.append([word, pos, kw[1]])
            noun_file.write(str([word, pos, kw[1]])+'\n')
        if pos in adj:
            adj_kw.append([word, pos, kw[1]])
            adj_file.write(str([word, pos, kw[1]])+'\n')
        if (not pos in noun) and (not pos in adj):
            other_kw.append([word, pos, kw[1]])
            other_file.write(str([word, pos, kw[1]])+'\n')
    f.write(str([word, pos, kw[1]])+'\n')
