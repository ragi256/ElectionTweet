#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson
import MeCab
import re
import os
import time
import gzip
from multiprocessing import Pool
from distributer import Distributer

#filter_list = []  あからさまに関係ないツイートでもフィルターにはかけない
hinshi_list = ['名詞']#,'動詞','形容詞']
link_pattern = re.compile ('(https?://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)')
query_list = ['賛成','反対']

def httpFilter(line):
    if "http" in line:
        temp = line
        line = link_pattern.sub(u"", temp)
    return line

def preformat(line):
    """一行を受け取り形態素解析をしてリストを返す
       連続した名詞はできるだけ長くなるように結合する
       見やすいように名詞であっても記号は取り除く"""
    line = re.sub(re.compile("[!-/:-@[-`{-~]"), ' ', line)
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


def function1(line):
    dist = Distributer()
    dist.reset()
    tweet_text = setTweet(line)
    if dist.isAboutElection(tweet_text,query_list):
        dist.extractToElection(tweet_text)
    else:
        dist.extractToAll(tweet_text)
    progress()
    #if dist.passElection() != []:
    #    print ",".join(dist.passElection())
    return list(set(dist.passElection() ) )

def function2(line):
    appearance_list = []
    tweet_text = setTweet(line)
    for query in relevant_word_list:
        for word in tweet_text:
            if word.find(query)!=-1:
                appearance_list.append(query)
#                break
    progress()
    #if appearance_list != []:
    #    print ",".join(appearance_list)
    return list(set(appearance_list))


def progress():
    import __main__
    if counter%tenth == 0:
        prog = "%s" % ("=" * (counter/tenth) + ">")
        print prog + '\r',
    __main__.counter += 1
    
def listsToDict(lists,dictionary):
    for list in lists:
        for word in list:
            if word in dictionary.keys():
                dictionary[word] += 1
            else:
                dictionary[word] = 1

def writeOutput(output,dictionary,top_line):
    counter = 0
    output.write(top_line)
    for key,value in sorted(dictionary.items(),key=lambda x:x[1],reverse=True):
        counter += 1
        output.write(str(counter) + ':' + key + '\t' + str(value) +'\n')
    output.write('\n')

def separete2Lists(results_tuples,listsA,listsB):
    for tupl in results_tuples:
        listsA.append(tupl[0])
        listsB.append(tupl[1])

def writeProbabilityDict(output,dictionary,total_tweet,string):
    probability_dict = {}
    for key,value in dictionary.items():
        probability_dict[key] = float(value) / total_tweet
        # if probability_dict[key] < 0.00001:
        #     del probability_dict[key]
        #     break
    writeOutput(output,probability_dict,string)

    
def main():
    print   '何プロセス走らせますか？ ',
    prosess = input()
    if prosess < 10: 10
    starttime = time.time()
    Input = open(argv[1], 'r')
    output= open(argv[2], 'w')
    total_tweet = sum(1 for line in Input)
    print argv[1] + 'は' + str(total_tweet) + '行あります'

    global tenth,counter
    tenth = total_tweet / 100
    
    counter = 0
    print '関連語抽出処理を開始します'
    Input.seek(0)
    pool = Pool(prosess)
    relevant_lists = pool.map(function1,Input)
    print 
    print '得られたリストを辞書に直します'
    relevant_dict = {}
    listsToDict(relevant_lists, relevant_dict)
    # print 'データを出力します'
    # write_line = "========== words around Election ==========\n"
    # writeOutput(output,relevant_dict,write_line)

    global relevant_word_list
    relevant_word_list = relevant_dict.keys()
    
    counter = 0
    print '関連語登場回数測定を開始します'
    Input.seek(0)
    pool = Pool(prosess)
    appear_rate_lists = pool.map(function2,Input)
    print
    print '得られたリストを辞書に直します'
    appear_rate_dict = {}
    listsToDict(appear_rate_lists, appear_rate_dict)
    print 'データを出力します'
    # write_line = "========== appear rate relevant word ==========\n"
    # writeOutput(output,appear_rate_dict,write_line)

    write_line = "========== relevant word & query tweet appear probability ==========\n"
    writeProbabilityDict(output,relevant_dict,total_tweet,write_line)
    write_line = "========== relevant word all tweet  appear probability ==========\n"
    writeProbabilityDict(output,appear_rate_dict,total_tweet,write_line)
 
    Input.close()
    output.close()
    
    endtime = time.time()
    print "time.time:",
    print endtime-starttime
    
if __name__ == '__main__':
    import sys
    argv = sys.argv
    main()
