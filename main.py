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


dist = Distributer()

# def function1(line):
#     tweet = simplejson.loads(line,"utf-8")
#     tweet["text"] = httpFilter(tweet["text"])
#     tweet_text = preformat(tweet["text"])[:-1]
#     if dist.isAboutElection(tweet_text,query_list):
#         dist.extractToElection(tweet_text)
#     else:
#         dist.extractToAll(tweet_text)
#     return dist.passElection()

# def wrapper(key):
#     appearance = 0
#     appear_rate_list = pool.map(function2,relevant_Dict.keys())
#     tweet = simplejson.loads(line,"utf-8")
#     tweet["text"] = httpFilter(tweet["text"])
#     tweet_text = preformat(tweet["text"])[:-1]
#     if key in tweet_text:

#     appearance += 1

        
#     return appearance



    
def main():
    starttime = time.clock()

    Input = open(argv[1], 'r')
    output= open(argv[2], 'w')

    pool = Pool(10)
    relevant_lists = pool.map(function1,Input)

    relevant_dict = {}
    for relevant_list in relevant_lists:
        for word in relevant_list:
            word = word.encode('utf-8')
            if word in relevant_dict.keys():
                relevant_dict[word] += 1
            else:
                relevant_dict[word] = 1

    output.write("\n========== words around Election ==========\n")
    for key,value in sorted(rlevant_dict.items(),key=lambda x:x[1],reverse=True):
        output.write(key + ':' + str(value) + '  ',)
    output.write('\n')

    Input.close()
    output.close()
    
    # for key in relevant_dict.keys():
        
    #     appear_rate = wrapper(key)


    # appear_rate_dict = {}    
        
    endtime = time.clock()
    print "time.clock:",
    print endtime-starttime
    
if __name__ == '__main__':
    import sys
    argv = sys.argv
    main()
