from __future__ import division
import numpy
import editdistance
import os
from setup import setup_fren


config   = setup_fren()
baseline = False

if not baseline:
    home = config['trans_to'] + '.split'
else:
    home = '../.translate/baseline_fren.valid.split'

if not os.path.exists(home):
    os.makedirs(home)


fr_list = []
with open(config['valid_datasets'][0], 'rb') as f:
    while True:
        ss = f.readline()
        if ss == '':
            break
        fr_list.append(ss)

fr_match_list = []
with open(config['valid_datasets'][2], 'rb') as f:
    while True:
        ss = f.readline()
        if ss == '':
            break
        fr_match_list.append(ss)

scores = []

for i in numpy.arange(len(fr_list)):
    score = editdistance.eval(fr_list[i].split() , fr_match_list[i].split())
    length_fr = len(fr_list[i].split())
    length_fr_match = len(fr_match_list[i].split())
    max_length = numpy.maximum(length_fr, length_fr_match)
    scores.append(1-score/max_length)

# print scores
index =[[] for i in numpy.arange(10)]
for i in numpy.arange(10):
    for j in numpy.arange(len(scores)):
        if i/10 < scores[j] <= (i+1)/10:
            index[i].append(j)
for i in numpy.arange(10):
    print len(index[i])


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> #
en_list = []
with open(config['valid_datasets'][1], 'rb') as f:
    while True:
        ss = f.readline()
        if ss == '':
            break
        en_list.append(ss)
en_trans_list = []

if not baseline:
    target = config['trans_to']
else:
    target = '../.translate/baseline_fren.valid'

with open(target, 'rb') as f:
    while True:
        ss = f.readline()
        if ss == '':
            break
        en_trans_list.append(ss)
en_sort_list = [[] for i in numpy.arange(10)]
en_trans_sort_list = [[] for i in numpy.arange(10)]
for i in numpy.arange(len(index)):
    for j in index[i]:
        en_sort_list[i].append(en_list[j])
        en_trans_sort_list[i].append(en_trans_list[j])

for i in numpy.arange(len(index)):
    with open(home + '/en_sort_'+ str(i), 'w') as f:
        for j in en_sort_list[i]:
            f.write(j)
    with open(home + '/en_trans_sort_'+ str(i), 'w') as f:
        for j in en_trans_sort_list[i]:
            f.write(j)



print 'compute BLEU scores for each of the files.'
hyp = []
ref = []
for i in numpy.arange(10):
    hyp.append(home + '/en_sort_'+str(i))
    ref.append(home + '/en_trans_sort_'+str(i))

for i in numpy.arange(10):
    os.system('perl ./data/multi-bleu.perl {0} < {1} | tee {1}.score'.format(ref[i], hyp[i]))
print 'done'

