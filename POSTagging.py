import glob
import nltk
from collections import Counter,OrderedDict
import json
from copy import deepcopy
import io

with open("./Data/vocab.json","r") as f:
  d = f.read()
vocab=json.loads(d)
with open("./Data/all_tags.json","r") as f:
  d = f.read()
all_tags=json.loads(d)
with open("./Data/tags_words_bigram.json","r") as f:
  d = f.read()
tags_words_bigram=json.loads(d)
with open("./Data/tags_tags_bigram.json","r") as f:
  d = f.read()
tags_tags_bigram=json.loads(d)
with open("./Data/count_tag_tag.json","r") as f:
  d = f.read()
count_tag_tag=json.loads(d)
with open("./Data/count_tag_output.json","r") as f:
  d = f.read()
count_tag_output=json.loads(d)
with open("./Data/sum_for_tag_op.json","r") as f:
  d = f.read()
sum_for_tag_op=json.loads(d)

### Test

f = open("./test_set.txt") ## test file
array = f.read().splitlines() ## one word per line
original = deepcopy(array)

temp=[]
for i in range(len(array)):
    if(array[i]!=''):
        array[i]= array[i].lower()
        if(array[i]=='.' or array[i]=='!' or array[i] =='?'):
            array[i]='<s>'

for i in array:
    if(i!=''):
        temp.append(i)

array=deepcopy(temp)

temp.clear()

for i in original:
    if(i!=''):
        temp.append(i)
original=deepcopy(temp)

# for ind in blank_indices:
#     del array[ind]
#     del original[ind]
# print(blank_indices)
# print(array)

# demo = "I am a pro programmer ! I hate coding ."
# demo = demo.lower()
# array = demo.split() 
# original = demo.split()
# for i in range(len(array)):
#     if(array[i]=='.' or array[i]=='!' or array[i] =='?'):
#         array[i]='<s>'


### EX-TEST now TRAIN
# sum_for_tag_op={}
# for item in count_tag_output:
#     sum=0
#     for occur_word in count_tag_output[item]:
#         sum+=(count_tag_output[item][occur_word]+1)
#     sum_for_tag_op[item]=sum

# for i in tags_tags_bigram:
#     for item in array:
#         if(item not in count_tag_output[i]):
#             count_tag_output[i][item]=0

for item in count_tag_output:
    sum = 0
    for occur_word in count_tag_output[item]:
        sum+=(count_tag_output[item][occur_word]+1)
    for occur_word in count_tag_output[item]:
        count_tag_output[item][occur_word]+=1            
        count_tag_output[item][occur_word]/=sum

viterbi={}

backpointers={} ## key is a string concat of state and observ

for states in count_tag_tag:
    viterbi[states]={}
    viterbi[states]['start']=0
    viterbi[states]['end']=0
    for observation in array:
        viterbi[states][observation]=0

for states in count_tag_tag['<s>']:## states now has the list of tags which have <s> as the preceeding tag
    viterbi[states][array[0]]=count_tag_tag['<s>'][states] ## transitional prob
    viterbi[states][array[0]]*=count_tag_output[states][array[0]] ## to be handled for UNK
    # print(states+" "+str(viterbi[states][array[0]])) recent

for i in range(1,len(array)): ## iterating through the other observation states
    prob={}
    for tag in viterbi:
        prob[tag]={}
        max = -1
        bestTag = ""
        for prev_tag in viterbi:
            ## consider all the possible places from which it is made
            prob[tag][prev_tag]=(viterbi[prev_tag][array[i-1]])
            prob[tag][prev_tag]*=count_tag_tag[prev_tag][tag]
            if(array[i] in count_tag_output[tag]):
                prob[tag][prev_tag]*=(count_tag_output[tag][array[i]])
            else:
                prob[tag][prev_tag]*=1/sum_for_tag_op[tag]
            if(max<prob[tag][prev_tag]):
                max = prob[tag][prev_tag]
                bestTag=prev_tag
        viterbi[tag][array[i]]=max
        key = tag+" "+str(i)
        bestTag+=(" "+str(i-1))
        backpointers[key]=bestTag

count_end_with_s={}
sum=0
for states in count_tag_tag:
    if(states in count_end_with_s):
        count_end_with_s[states]['<s>']+=(count_tag_tag[states]['<s>']+1)
    else:
        count_end_with_s[states]={}
        count_end_with_s[states]['<s>']=(count_tag_tag[states]['<s>']+1)
    sum+=(count_end_with_s[states]['<s>'])
for states in count_tag_tag:
    if('<s>' in count_tag_tag[states]):
        if(sum>0):
            count_end_with_s[states]['<s>']/=sum
        else:
            print("Zero Sum error")
highest_prob_tag=""
highest_prob_tag_value=-1

for states in count_tag_tag:
    viterbi[states]['end']=count_end_with_s[states]['<s>']
    viterbi[states]['end']*=viterbi[states][array[len(array)-1]]
    if(viterbi[states]['end']>highest_prob_tag_value):
        highest_prob_tag_value=viterbi[states]['end']
        highest_prob_tag=states

# print(array[len(array)-1]+" "+highest_prob_tag)
i=len(array)-1
# print(backpointers)
stack=[]
while(i>=0):
    printable_op=highest_prob_tag
    if(highest_prob_tag=='<s>'):
        printable_op='.' ## map to original tag input
    stack.append(original[i]+"\t"+str(printable_op))
    if(i>0):
        prev_best_tag = backpointers[highest_prob_tag+" "+str(i)]
        prev = prev_best_tag.split()
        highest_prob_tag=prev[0]
    i-=1
while(len(stack)>0):
    print(stack.pop())