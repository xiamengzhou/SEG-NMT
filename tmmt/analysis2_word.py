from __future__ import division
import numpy
import os
import  pickle as pkl
import matplotlib.pylab as plt

# file_list =[[]]*len(range(2500, 10000, 2500))
file_list_word = []
for j, i in enumerate(range(2500, 162500, 2500)):
    file = open('/root/workspace/TMNMT/.translate/TM2.B7.dev.translate.iter='+str(i)+'.pkl', 'r')
    file_list_word.append(pkl.load(file))    
    print(i)
    
action_word = [[] for _ in range(len(file_list_word))]
gating_word = [[] for _ in range(len(file_list_word))]
# print action
# print len(file_list)
# print len(file_list[0])
# print len(file_list[0][0])
# print len(file_list[0][0][0])
# print file_list[0][1][2]
# print file_list[1][1][2]


for i in range(len(file_list_word)):
    for j in range(len(file_list_word[i])):
#         print len(file_list[i][0])
        action_word[i].append(file_list_word[i][j][2])
        gating_word[i].append(file_list_word[i][j][3])

# print action
aver_action_word = []
aver_gating_word = []
# print len(action[0])
# print len(action[1])
# print len(action[0][0])
# print len(action[0][1])
# print len(action[0][2])
# print len(action[1][0])
# print len(action[1][1])
# print len(action[1][2])
# print action[0][0]
# print action[1][0]
for i in range(len(file_list_word)):
    action_init = []
    gating_init = []
    for j in range(len(action[i])):
        
        action_init += action[i][j]
        gating_init += gating[i][j]

    aver_action_word.append(numpy.asarray(action_init).mean())
    aver_gating_word.append(numpy.asarray(gating_init).mean())

print aver_action_word
print aver_gating_word
plt.plot(range(2500, 162500, 2500),aver_action_word, '-b',label='aver-action')
plt.plot(range(2500, 162500, 2500),aver_gating_word,  '-r', label='aver-gating')
plt.xlabel('Number of updates')
plt.ylim(0,1)
plt.legend()
plt.savefig('/root/workspace/TMNMT/dl4mt-tm2/Myfig_word.jpg')       
    