#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson
import MeCab
import re
import os
import time
import gzip
#import multiprocessing
from multiprocessing import Pool
from distributer import Distributer

#filter_list = []  あからさまに関係ないツイートでもフィルターにはかけない
hinshi_list = ['名詞','動詞','形容詞']
link_pattern = re.compile ('(https?://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)')
query_list = ['賛成','反対']

def httpFilter(line):
    if "http" in line:
        temp = line
        line = link_pattern.sub(u"", temp)
    return line

def preformat(line):
    """一行を受け取り形態素解析をしてリストを返す
       連続した名詞はできるだけ長くなるように結合する"""
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
    tweet["text"] = httpFilter(tweet["text"])
    tweet_text = preformat(tweet["text"])[:-1]
    return tweet_text

dist = Distributer()
def function1(line):
    import __main__
    tweet_text = setTweet(line)
    if dist.isAboutElection(tweet_text,query_list):
        dist.extractToElection(tweet_text)
    else:
        dist.extractToAll(tweet_text)
    if counter%tenth == 0:
        prog = "%s" % ("=" * (counter/tenth) + ">")
        print prog + '\r',
    __main__.counter += 1
    return dist.passElection()

def function2(line):
    import __main__
    appearance_list = []
    tweet_text = setTweet(line)
    for query in relevant_word_list:
        for word in tweet_text:
            if word.find(query)!=-1:
                appearance_list.append(query)
    if counter%tenth == 0:
        prog = "%s" % ("=" * (counter/tenth) + ">")
        print prog + '\r',
    __main__.counter += 1
    appearance_list = list(set(appearance_list))
    # if appearance_list != []:
    #     print ",".join(appearance_list)
    return appearance_list

def lists2dict(lists,dictionary):
    for list in lists:
        for word in list:
            if word in dictionary.keys():
                dictionary[word] += 1
            else:
                dictionary[word] = 1

def main():
    starttime = time.clock()
    global Input
    Input = open(argv[1], 'r')
    output= open(argv[2], 'w')
    total_tweet = sum(1 for line in Input)
    print argv[1] + 'は' + str(total_tweet) + '行あります'

    global tenth,counter
    tenth = total_tweet / 100
    
    counter = 0
    print '関連語抽出処理を開始します'
    Input.seek(0)
    pool = Pool(10)
    relevant_lists = pool.map(function1,Input)
    print 
    
    relevant_dict = {}
    lists2dict(relevant_lists, relevant_dict)

    counter = 0
    output.write("========== words around Election ==========\n")
    for key,value in sorted(relevant_dict.items(),key=lambda x:x[1],reverse=True):
        counter += 1
        output.write(str(counter) + ':' + key + '\t' + str(value) + '\n')
    output.write('\n')

    global relevant_word_list
    relevant_word_list = relevant_dict.keys()
    
    counter = 0
    print '関連語登場回数測定を開始します'
    Input.seek(0)
    pool = Pool(10)
    appear_rate_lists = pool.map(function2,Input)
    print
    
    appear_rate_dict = {}
    lists2dict(appear_rate_lists, appear_rate_dict)

    counter = 0
    output.write("========== appear rate relevant word ==========\n")
    for key,value in sorted(appear_rate_dict.items(),key=lambda x:x[1],reverse=True):
        counter += 1
        output.write(str(counter) + ':' + key + '\t' + str(value) + '\n')

    Input.close()
    output.close()
    
    endtime = time.clock()
    print "time.clock:",
    print endtime-starttime
    
if __name__ == '__main__':
    import sys
    argv = sys.argv
    main()
