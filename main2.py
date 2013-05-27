#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson
import MeCab
import re
import sys
import os
import time
import gzip
import copy
from decimal import *
from multiprocessing import Process, Manager
from distributer import Distributer

#filter_list = ['AKB']  あからさまに関係ないツイートでもフィルターにはかけない
hinshi_list = ['名詞']#,'動詞','形容詞']
http_filter_pattern = re.compile ('(https?://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)')
string_filter_pattern = re.compile (u'([0-9A-Za-z⺀-⿕ぁ-ヾ㐀-䶵一-龥豈-舘０-９Ａ-Ｚａ-ｚｦ-ﾝ]+)')
query_list = ['賛成','反対']

def stringFilter(line):
    line = http_filter_pattern.sub(" ", line)
    line = string_filter_pattern.findall(line)
    line = u"、".join(line)
    return line

def preformat(line):
    """一行を受け取り形態素解析をしてリストを返す
       連続した名詞はできるだけ長くなるように結合する
       見やすいように名詞であっても記号は取り除く"""
    tagger = MeCab.Tagger('')
    encoded_line = line.encode('utf-8')
    node = tagger.parseToNode(encoded_line)
    keywords =[]
    while node:
        node_f = node.feature.split(",")
        hinshi = node_f[0]
        genkei = node_f[6]
        if hinshi in hinshi_list:
            if genkei == "*":
                genkei = node.surface
            elif previous=='名詞' and hinshi=='名詞':
                genkei = keywords.pop() + genkei
            keywords.append(genkei)
        previous = hinshi
        node = node.next
    return keywords

def setTweet(line):
    tweet = simplejson.loads(line,"utf-8")
    tweet["text"] = stringFilter(tweet["text"])
    tweet_text = preformat(tweet["text"])[:-1]
    return tweet_text

def function1(line,dictionary,tenth):
    dist = Distributer()
    tweet_text = setTweet(line)
    if dist.isAboutElection(tweet_text,query_list):
        dist.extractToElection(tweet_text)
    else:
        dist.extractToAll(tweet_text)
    progress(tenth)
    #if dist.passElection() != []:
    #    print ",".join(dist.passElection())
    election = list(set(dist.passElection()))
    listToDict(election,dictionary)
    
def function2(line,dictionary,relevant_word_list,tenth):
    appearance_list = []
    tweet_text = setTweet(line)
    for query in relevant_word_list:
        for word in tweet_text:
            if word.find(query)!=-1:
                appearance_list.append(query)
                break
    progress(tenth)
    #if appearance_list != []:
    #    print ",".join(appearance_list)
    appearance_list = list(set(appearance_list))
    listToDict(appearance_list,dictionary)
    
def progress(tenth):
    import __main__
    if __main__.counter%tenth == 0:
        prog = "%s" % ("=" * (__main__.counter/tenth) + ">")
        print prog + '\r',
    __main__.counter += 1
    
def listsToDict(lists,dictionary):
    for list in lists:
        listToDict(list,dictionary)
        
def listToDict(list,dictionary):
        for word in list:
            if word in dictionary.keys():
                dictionary[word] += 1
            else:
                dictionary[word] = 1

def writeProbabilityDict(output,dictionary,total_tweet,string):
    probability_dict = {}
    for key,value in dictionary.items():
        probability_dict[key] = Decimal(value) / total_tweet
    writeOutput(output,probability_dict,string)

def writeOutput(output,dictionary,top_line):
    counter = 0
    output.write(top_line)
    for key,value in sorted(dictionary.items(),key=lambda x:x[1],reverse=True):
        counter += 1
        output.write(str(counter) + ':' + key + '\n\t\t' + str(value) +'\n')
    output.write('\n')
    
if __name__ == '__main__':
    argv = sys.argv
    starttime = time.time()
    manager = Manager()
    Input = gzip.open(argv[1], 'r')
    output1 = open(argv[2], 'w')
    output2 = open(argv[3], 'w') 
    total_tweet = sum(1 for line in Input)
    print argv[1] + 'は' + str(total_tweet) + '行あります'
    global counter
    tenth = total_tweet / 100    
    counter = 0

    print '関連語抽出処理を開始します'
    Input.seek(0)
    relevant_dict = manager.dict()
    for line in Input:
        p = Process(target=function1, args=(line,relevant_dict,tenth))
        p.start()
    p.join()

    print 'データを出力します'
    write_line = "========== relevant word & query tweet appear probability ==========\n"
    writeProbabilityDict(output1,relevant_dict,total_tweet,write_line)
    
    counter = 0
    print '関連語登場回数測定を開始します'
    Input.seek(0)
    appear_rate_dict = manager.dict()
    for line in Input:
        p = Process(target=function2, args=(line,appear_rate_dict,relevant_dict.keys(),tenth))
        p.start()
    p.join()

    print 'データを出力します'
    write_line = "========== relevant word all tweet  appear probability ==========\n"
    writeProbabilityDict(output2,appear_rate_dict,total_tweet,write_line)
 
    Input.close()
    output1.close()
    output2.close()
    
    endtime = time.time()
    print "time.time:",
    print endtime-starttime

