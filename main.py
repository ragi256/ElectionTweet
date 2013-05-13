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
    """一行を受け取り形態素解析をしてリストを返す"""
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

def function(line):
    tweet = simplejson.loads(line,"utf-8")
    tweet["text"] = httpFilter(tweet["text"])
    tweet_text = preformat(tweet["text"])[:-1]
    if dist.isAboutElection(tweet_text,query_list):
        dist.extractToElection(tweet_text)
    else:
        dist.extractToAll(tweet_text)
    return dist.passElection()
    
def main():
    starttime = time.clock()

    input = open(argv[1], 'r')
    output= open(argv[2], 'w')

    pool = Pool(10)
    dictionaryList = pool.map_async(function,input)

    resultDict = {}
    for dictionary in dictionaryList.get():
        for key,value in dictionary.items():
            if key in resultDict:
                resultDict[key] += value
            else:
                resultDict[key] = 1

    output.write("\n========== words around Election ==========\n")
    for key,value in sorted(resultDict.items(),key=lambda x:x[1],reverse=True):
        output.write(key + ':',)
        output.write(str(value),)
        output.write('  ',)
    output.write('\n')

    input.close()
    output.close()
    
    endtime = time.clock()
    print "time.clock:",
    print endtime-starttime
    
if __name__ == '__main__':
    import sys
    argv = sys.argv
    main()
