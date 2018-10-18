import glob
import nltk
from collections import Counter,OrderedDict
import json
from copy import deepcopy
import io

f = open("./Training set_HMM.txt")

all_words = []
x = f.read().splitlines()
for line in x:
    words = line.split('\t')
    for w in words:
        if(w!=''):
            all_words.append(w)

vocab={}  ### maintains words and their occurence counts
all_tags={} ### maintains tags and their occurence counts 
tags_words_bigram={} ## dictionary with tags as key and list as value with all the words having that tag
tags_tags_bigram={} ## dictionary with tag(i-1) and tag(i); tag(i-1) is the key and value is array of tag(i)

i=1
prev_tag = '<s>'
while((i)<len(all_words)):
    tag = all_words[i]
    if(tag in all_tags):
        all_tags[tag]+=1
    else:
        all_tags[tag]=0
    word = all_words[i-1]
    if(word in vocab):
        vocab[word]+=1
    else:
        vocab[word]=0
    if(i>=2):
        prev_tag = all_words[i-2]
    if(word=='.' or word=='?' or word=='!'):
        word='<s>'
    if(tag=='.' or tag=='?' or tag=='!'):
        tag='<s>'
    if(tag in tags_words_bigram):
        tags_words_bigram[tag].append(word)
    else:
        tags_words_bigram[tag]=[]
        tags_words_bigram[tag].append(word)
    if(prev_tag in tags_tags_bigram):
        tags_tags_bigram[prev_tag].append(tag)
    else:
        tags_tags_bigram[prev_tag]=[]
        tags_tags_bigram[prev_tag].append(tag)
    i+=2
tags_tags_bigram['<s>']=[]
# print(tags_tags_bigram['.'])
if('.' in tags_tags_bigram):
    for tag in tags_tags_bigram['.']:
        tags_tags_bigram['<s>'].append(tag)
if('!' in tags_tags_bigram):
    for tag in tags_tags_bigram['!']:
        tags_tags_bigram['<s>'].append(tag)
if('?' in tags_tags_bigram):
    for tag in tags_tags_bigram['?']:
        tags_tags_bigram['<s>'].append(tag)
tags_tags_bigram.pop('!',None)
tags_tags_bigram.pop('.',None)
tags_tags_bigram.pop('?',None)

count_tag_tag={}  ## key = tag, value is dict with key as tag and value as count
count_tag_output={}  ## key = tag, value is dict with key as output and value as count

## creating count_tag_tag
for item in tags_tags_bigram:
    count_tag_tag[item]={}
    for i in tags_tags_bigram:
        count_tag_tag[item][i]=0
for item in tags_tags_bigram:
    for occurence in tags_tags_bigram[item]:
        if(occurence in count_tag_tag[item]):
            count_tag_tag[item][occurence]+=1
        else:
            count_tag_tag[item][occurence]=0

### normalise to get probab
for item in count_tag_tag:
    sum = 0
    for occur_tag in count_tag_tag[item]:
        sum+=(count_tag_tag[item][occur_tag]+1)
    for occur_tag in count_tag_tag[item]:
        if(sum!=0):
            count_tag_tag[item][occur_tag]+=1
            count_tag_tag[item][occur_tag]/=sum
        else:
            print("tag: "+item+" occur_tag: "+occur_tag+" Jeter") ## Comment

## initialisation of tag output dict prob
for i in tags_tags_bigram:
    count_tag_output[i]={}
    for item in vocab:
        if(item=='.' or item=='!' or item=='?'):
            item = '<s>'
        count_tag_output[i][item]=0
    # for item in array:
    #     if(item not in count_tag_output[i]):
    #         count_tag_output[i][item]=0
for i in tags_tags_bigram:
    for occurence in tags_words_bigram[i]:
        if(occurence in count_tag_output[i]):
            count_tag_output[i][occurence]+=1
        else:
            print(occurence in vocab)
            print(i+" "+occurence+ " Not there")

sum_for_tag_op={}
for item in count_tag_output:
    sum=0
    for occur_word in count_tag_output[item]:
        sum+=(count_tag_output[item][occur_word]+1)
    sum_for_tag_op[item]=sum

with open('./Data/vocab.json','w') as fp:
    json.dump(vocab, fp)
with open('./Data/all_tags.json','w') as fp:
    json.dump(all_tags, fp)
with open('./Data/tags_words_bigram.json','w') as fp:
    json.dump(tags_words_bigram,fp)
with open('./Data/tags_tags_bigram.json','w') as fp:
    json.dump(tags_tags_bigram,fp)
with open('./Data/count_tag_tag.json','w') as fp:
    json.dump(count_tag_tag,fp)
with open('./Data/count_tag_output.json','w') as fp:
    json.dump(count_tag_output,fp)
with open('./Data/sum_for_tag_op.json','w') as fp:
    json.dump(sum_for_tag_op,fp)